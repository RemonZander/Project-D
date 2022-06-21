from re import U
from unittest import result
from flask import Flask, request, Response
import concurrent.futures
#from flask_socketio import SocketIO
from enum import Enum
from flask_tcp_client import *
from image_validation import *
import threading
import socket
import json
from MessageType import MessageType
from Message import Message
import time
from time import sleep
import base64

#USER CONNECTS
#NEW THREAD
#SEE IF THERE ARE ANY GAPS IN GIVEN INDEXES (TRACKED BY AVAILABLE INDEXES)
#   IF SO:
#       user_id = index_gap_list[0]
#       index_gap_list.remove(user_id) #REMOVE VALUE FROM GAP LIST (SHRINKS LIST)

#   ELSE:
#       user_id = ++highest_user_id #TODO: user id max limit?

#CREATE NEW EVENT AND ADD TO event_list AT INDEX user_id
#CALL WAIT ON THAT EVENT

#CALCULATION IS DONE, TCP CLIENT RELEASES THE EVENT AT INDEX user_id

#REMOVE user_id FROM EVENT LIST
#user_id == highest_user_id ?
#   IF SO:
#       ITERATE THROUGH event_list BACKWARDS STARTING AT user_id-1 TO FIND NEW highest_user_id
        #REMOVE ALL EMPTY INDEXES FOUND BEFORE NEW highest_user_id FROM index_gap_list
#   ELSE:
#       ADD user_id TO available_index list

#THREAD ENDS
#USER DISCONNECTS

#GLOBAL VARIABLES
event_list = [] #list[tuple(int, threading.Event)] 
tcp_result = ""
index_gap_list: int = []
highest_user_index: int = -1

event_list_lock = threading.Lock()
tcp_result_lock = threading.Lock()
index_gap_list_lock = threading.Lock()
highest_user_index_lock = threading.Lock()
tcp_client_lock = threading.Lock()

def search_event_by_user_index(user_index: int) -> threading.Event:
    """
    Iterates through global `event_list` and returns first instance where Item1 in tuple == `user_index`

    Parameters
    ---------
    - `user_index` (int): The index to be removed

    Returns
    ---------
    - threading.Event: Event which contains `user_index` as first value in it's tuple
    """
    global event_list
    for event in event_list:
        if event[0] == user_index:
            return event[1]

def remove_event_by_user_index(user_index: int) -> None:
    """
    Removes event which contains id `user_index` as first value in tuple from global `event_list`.

    Parameters
    ---------
    - `user_index` (int): The index to be removed

    Returns
    ---------
    - None
    """
    global event_list
    event_to_remove = ""
    for event in event_list:
        if event[0] == user_index:
            event_to_remove = event
            break
    event_list.remove(event_to_remove)

class FlaskHTTPServer():
    def __init__(self):
        self.app = Flask(__name__)
        self.app.add_url_rule("/image", "image", self.handle_extension_post, methods=["POST"])
        self.app.run(debug=True)

    def handle_extension_post(self):
        """
        Handles the endpoint `/image`

        Parameters
        ---------
        - None

        Returns
        ---------
        - self.handle_request()
        """
        if request.method == "POST":
            #print("FLASK SERVER: NEW CLIENT CONNECTING...")
            #sleep(10)
            #print("FLASK SERVER: CLIENT LEAVING...")
            
            #INPUT VALIDATION
            image = request.files["image"]
            print(type(image))
            if not validate_image(image):
                return {"errorCode": 415, "message": "The media format of the requested data is not supported by the server, so the server is rejecting the request." }, 415

            complex_case = request.form["complex_case"]
            print(f"IMAGE TYPE: {type(image)}")

            #TODO: RESCALE IMAGE, MAX IMAGE SIZE? 
            image_bytes = image.read()

            #print(len(image_bytes))
            return self.handle_request(image_bytes, complex_case)

    def handle_request(self, image_bytes : bytes, complex_case: bool) -> tuple():
        """
        Facilitates the request for the requesting user.
        Following sequence:
        - Assign user ID
        - Create new event using the ID
        - Forward the request to TCP client
        - Wait for msg to be returned
        - (msg received) Deallocate user ID
        - Converts return msg into response
        - Return response

        Parameters
        ---------
        - `image` (bytes): Image in raw byte format
        - `complex_case` (bool): Whether or not the process will follow complex or simple route (irrelevant for this method)

        Returns
        ---------
        - `tuple`: Tuple containing a dict storing the return code and return msg (e.g {"Code": 200, "Message": "})
                and the return code as int.
        """
        print("FLASK SERVER: HANDLING REQUEST...")
        print(f"FLASK SERVER: ACTIVE CONNECTIONS: {threading.activeCount() - 1}")
        user_index = self.allocate_user_index()

        event_list_lock.acquire()
        event_list.append((user_index, threading.Event()))
        event_list_lock.release()

        self.send_request_to_tcp(user_index, image_bytes, complex_case)
        msg = self.wait_for_event(user_index)
        self.deallocate_user_index(user_index)
        print(f"FLASK SERVER: USER {user_index} DONE.")
        return {"Code": 200, "Mmessage": "Message succesfully processed" }, 200 #TODO: Add msg in payload

    def allocate_user_index(self) -> int:
        """
        Assigns and returns a user index.
        If the global `index_gap_list` contains any index, returns `index_gap_list`[0].
        Else increases global `highest_user_index` by 1 and returns that outcome
        
        Parameters
        ---------
        - None

        Returns
        ---------
        - int: allocated user_index
        """
        print("FLASK SERVER: ALLOCATING USER_INDEX...")
        global highest_user_index
        global index_gap_list
        user_index = -1

        index_gap_list_lock.acquire()
        highest_user_index_lock.acquire()

        if len(index_gap_list) > 0:
            user_index = index_gap_list[0]
            index_gap_list.remove(user_index)
        else:
            user_index = highest_user_index + 1
            highest_user_index = user_index

        index_gap_list_lock.release()
        highest_user_index_lock.release()
        print(f"FLASK SERVER: GIVEN USER INDEX IS {str(user_index)}")
        return user_index

    def deallocate_user_index(self, user_index: int) -> None:
        """
        De-assigns a user index.
        If the `user_index` is currently the global `highest_user_index`,
        the function iterates through global `event_list` starting at `event_list`[-1] to find the next highest index. 
        If a new event is found, that event's index becomes the new `highest_user_index`.
        Else no new event in list, `highest_user_index` becomes `-1`.
        Parameters
        ---------
        - `user_index` (int): Index to deallocate

        Returns
        ---------
        - None
        """
        print("FLASK SERVER: DEALLOCATING USER_INDEX...")
        global highest_user_index
        global index_gap_list
        global event_list

        highest_user_index_lock.acquire()
        event_list_lock.acquire()
        index_gap_list_lock.acquire()

        if user_index == highest_user_index:
            for index in range(1, len(event_list)):
                if event_list[-index -1] is not None:
                    highest_user_index = event_list.index(event_list[-index -1])
                    event_list = event_list[0:highest_user_index+1]
                    break
                if index == len(event_list) - 1:
                    highest_user_index = -1
                    event_list = []
                    break
        else:
            index_gap_list.append(user_index)

        highest_user_index_lock.release()
        event_list_lock.release()
        index_gap_list_lock.release()

    def send_request_to_tcp(self, user_index: int, image: bytes, complex_case: bool) -> None:
        """
        Forward a request to a TCP client.

        Parameters
        ---------
        - `user_index` (int): User index to be forwarded
        - `image` (bytes): Image to be forwarded
        - `complex_case` (bool): Image to be forwarded

        Returns
        ---------
        - None
        """
        print("FLASK SERVER: SENDING REQUEST TO TCP...")
        tcp_client_lock.acquire()
        tcp_client.send_request(user_index, image, complex_case)
        tcp_client_lock.release()

    def wait_for_event(self, user_index: int) -> Message:
        """
        Blocks the thread until the event in global `event_list` with index `user_index` is set.
        When the event is set, the event gets removed from the `event_list`
        Contents of the event get retrieved and returned from global `tcp_result` 

        Parameters
        ---------
        - `user_index` (int): Index within global `event_list` to wait for

        Returns
        ---------
        - Message: Message found in the global `tcp_result`
        """
        global tcp_result
        global event_list

        print("FLASK SERVER: WAITING FOR EVENT...")
        event_list_lock.acquire()
        event = search_event_by_user_index(user_index)
        event_list_lock.release()

        event.wait() #TODO: Time-out period?
        print("FLASK SERVER: EVENT PROCESSED...")
        event_list_lock.acquire()
        remove_event_by_user_index(user_index)
        event_list_lock.release()

        msg = tcp_result
        tcp_result = "" #Empty result for security
        tcp_result_lock.release()

        return msg

#PORT MAPPINGS:
#CLIENT             -      SERVER                   :   PORT
#FLASK              -      TCP CONTROLLER           :   5050
#TCP CONTROLLER     -      IMAGE SEGMENTATION       :   5051
#TCP CONTROLLER     -      IMAGE CLASSIFICATION     :   5052
#TCP CONTROLLER     -      IMAGE COMPARER           :   5053

#ADDRESS_FLASK_TCP = (socket.gethostbyname(socket.gethostname()), 5050)

class FlaskTCPClient:
    def __init__(self, BUFFER_MAX=250000, PORT_FLASK_TCP=5050, SERVER=socket.gethostbyname(socket.gethostname()), FORMAT="utf-8"):
        self.BUFFER_MAX = BUFFER_MAX
        self.PORT_FLASK_TCP = PORT_FLASK_TCP #TODO: SEE IF 
        self.SERVER = SERVER
        self.ADDRESS_FLASK_TCP = (self.SERVER, self.PORT_FLASK_TCP)
        self.FORMAT = FORMAT
        self.client_amount = 0
        self.lock = threading.Lock()

        self.client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_tcp_client(self) -> None:
        """
        Connects `self.client` to `self.ADRESS_FLASK_TCP` as a client.
        Parameters
        ---------
        - None

        Returns
        ---------
        - None
        """
        print("TCP CLIENT: STARTING...")
        print(socket.gethostbyname(socket.gethostname()))
        self.client.connect(self.ADDRESS_FLASK_TCP)

    def send_request(self, user_index: int, image_bytes: bytes, complex_case: bool) -> None:
        """
        Sends a `Message` object containing given variables to `self.ADRESS_FLASK_TCP`

        Variables
        ---------
        - user_index (int): Attribtute for `Message` object to be sent
        - image_bytes (bytes): Attribtute for `Message` object to be sent
        - complex_cases (bool): Attribtute for `Message` object to be sent

        Returns
        ---------
        - None
        """
        print("TCP CLIENT: SENDING REQUEST...")
        self.lock.acquire()
        if self.client_amount == 0:
            thread = threading.Thread(target=self.listen) #args=(None))
            thread.start()
        self.client_amount += 1
        self.lock.release()

        image_base64 = base64.b64encode(image_bytes)
        image_ascii = image_base64.decode("ascii")
        msg = Message(user_index, image_ascii , complex_case) #TODO: Create message from image
        msg_json = msg.to_json()
        #CONVERT MSG TO BYTES
        converted_msg = msg_json.encode("ascii")
        print(f"TCP CLIENT: MESSAGE LENGTH: {len(converted_msg)}")
        
        """
        image_bytes_decoded = image_base64.decode("ascii")
        image_bytes = image_bytes_decoded.encode("ascii") #self.format
        #image_bytes_decoded.save("testsave.jpg")
        with open ("testimage.jpg", "wb") as b:
            print("writing")
            b.write(image_bytes)
            print("Written")



        msg = Message(user_index, image_bytes_decoded , complex_case) #TODO: Create message from image
        msg = msg.to_json()
        #CONVERT MSG TO BYTES
        converted_msg = msg.encode("ASCII")
        print(f"TCP CLIENT: MESSAGE LENGTH: {len(converted_msg)}")
        """
        #ADD PADDING TO MAKE MSG SIZE 250000
        converted_msg += b" " * (self.BUFFER_MAX - len(converted_msg))
        self.client.send(converted_msg)

    def listen(self) -> None:
        """
        Listens on `self..ADRESS_FLASK_TCP` as long as `self.client_amount` gt 0.
        When a message is received, global `tcp_result` gets assigned to the message. After which the event storing the same `user_index` from msg gets triggered.

        Variables
        ---------
        - None

        Returns
        ---------
        - None
        """
        global tcp_result
        global event_list

        print("TCP CLIENT: LISTENING TO RESPONSE...")
        #WAIT FOR RESPONSE
        while self.client_amount > 0:
            response = self.client.recv(self.BUFFER_MAX)
            if response:
                print("TCP CLIENT: RESPONSE RECEIVED...")
                #TODO: Error handling, validation
                msg = response.decode(self.FORMAT)
                print(f"TCP CLIENT: RESPONSE RECEIVED: {msg}")
                msg_json = json.loads(msg)
                msg_object = Message.from_json(msg_json)

                user_index = msg_object.user_index

                tcp_result_lock.acquire()
                tcp_result = msg_object

                event_list_lock.acquire()
                event = search_event_by_user_index(user_index)
                event.set()
                event_list_lock.release()

                self.lock.acquire()
                self.client_amount -= 1
                self.lock.release()



if __name__ == '__main__':
    tcp_client = FlaskTCPClient()
    tcp_client.start_tcp_client()
    flask_server = FlaskHTTPServer()
    #for _ in range(5):
        #flask_server.debug_func()

    #list = []
    #list.insert(4, "test")
    #print(list[0])
    #print(list[3])