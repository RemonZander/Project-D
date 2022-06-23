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
from exif_data import ExifData
from square_image import square_image
import os

#USER CONNECTS
#NEW THREAD
#SEE IF THERE ARE ANY GAPS IN GIVEN INDEXES (TRACKED BY AVAILABLE INDEXES)
#   IF SO:
#       user_id = id_gap_list[0]
#       id_gap_list.remove(user_id) #REMOVE VALUE FROM GAP LIST (SHRINKS LIST)

#   ELSE:
#       user_id = ++highest_user_id #TODO: user id max limit?

#CREATE NEW EVENT AND ADD TO event_list AT INDEX user_id
#CALL WAIT ON THAT EVENT

#CALCULATION IS DONE, TCP CLIENT RELEASES THE EVENT AT INDEX user_id

#REMOVE user_id FROM EVENT LIST
#user_id == highest_user_id ?
#   IF SO:
#       ITERATE THROUGH event_list BACKWARDS STARTING AT user_id-1 TO FIND NEW highest_user_id
        #REMOVE ALL EMPTY INDEXES FOUND BEFORE NEW highest_user_id FROM id_gap_list
#   ELSE:
#       ADD user_id TO available_index list

#THREAD ENDS
#USER DISCONNECTS

#GLOBAL VARIABLES
event_list = []
tcp_result = ""

event_list_lock = threading.Lock()
tcp_result_lock = threading.Lock()
tcp_client_lock = threading.Lock()

def get_event_by_user_id(user_id:int):
    """
    Returns an event which from the tuple in global `event_list` which contains `user_id` as Item1 in the tuple

    Parameters
    ---------
    - `user_id` (int): The number to search for in global `event_list`

    Returns
    ---------
    - threading.event : Event found
    - False : No event found
    """
    print(event_list)
    for event in event_list:     
        if event[0] == user_id:
            return event
    #return False

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
        if request.method != "POST": return {"Code": 400, "message": "Request type not accepted" }, 400

        #INPUT VALIDATION
        image = request.files["image"]
        print(type(image))
        if not validate_image(image):
            return {"Code": 415, "message": "The media format of the requested data is not supported by the server, so the server is rejecting the request." }, 415

        print("FLASK SERVER: HANDLING REQUEST...")
        return self.__handle_request(image.read(), request.form["complex_case"])
        
    def __allocate_user_id(self) -> int:
        """
        Assigns and returns a user index.
        Iterates through global `event_list` to find the current highest "user_id".
        Returns the highest user id + 1.
        
        Parameters
        ---------
        - None

        Returns
        ---------
        - int: allocated user_id
        """
        print("FLASK SERVER: ALLOCATING user_id...")
        global event_list

        event_list_lock.acquire()
        assigned_user_id = 0
        for tuple_id_event in event_list:
            if tuple_id_event[0] > assigned_user_id:
                assigned_user_id = tuple_id_event[0] +1

        event_list_lock.release()
        print(f"FLASK SERVER: GIVEN USER INDEX IS {str(assigned_user_id)}")
        return assigned_user_id

    def __remove_event_by_user_id(user_id: int) -> None:
        """
        Removes event which contains id `user_id` as first value in tuple from global `event_list`.

        Parameters
        ---------
        - `user_id` (int): The index to be removed

        Returns
        ---------
        - None
        """
        global event_list
        event_to_remove = ""
        for event in event_list:
            if event[0] == user_id:
                event_to_remove = event
                break
        event_list.remove(event_to_remove)

    """
    def __deallocate_user_id(self, user_id: int) -> None:
        #
        #De-assigns a user index.
        #If the `user_id` is currently the global `highest_user_id`,
        #the function iterates through global `event_list` starting at `event_list`[-1] to find the next highest index. 
        #If a new event is found, that event's user_id becomes the new `highest_user_id`.
        #Else no new event in list, `highest_user_id` becomes `-1`.
        #Parameters
        #---------
        #- `user_id` (int): Index to deallocate

        #Returns
        #---------
        #- None
        #
        print("FLASK SERVER: DEALLOCATING user_id...")
        global highest_user_id
        global id_gap_list
        global event_list

        highest_user_id_lock.acquire()
        event_list_lock.acquire()
        id_gap_list_lock.acquire()

        if user_id == highest_user_id:
            if len(event_list) == 1:
                highest_user_id = -1
            else:
                new_highest_user_id = -1
                for index in range(1, len(event_list)):
                    if event_list[-index -1][0] > new_highest_user_id:
                        new_highest_user_id = event_list[-index -1][0]
                highest_user_id = new_highest_user_id
        else:
            id_gap_list.append(user_id)

        highest_user_id_lock.release()
        event_list_lock.release()
        id_gap_list_lock.release()
    """

    def __wait_for_event(self, user_id: int) -> Message:
        """
        Blocks the thread until the event in global `event_list` with index `user_id` is set.
        When the event is set, the event gets removed from the `event_list`
        Contents of the event get retrieved and returned from global `tcp_result` 

        Parameters
        ---------
        - `user_id` (int): Index within global `event_list` to wait for

        Returns
        ---------
        - Message: Message found in the global `tcp_result`
        """
        global tcp_result
        global event_list
        user_event = []

        print("FLASK SERVER: WAITING FOR EVENT...")
        event_list_lock.acquire()
        
        user_event = get_event_by_user_id(user_id)[1]
        event_list_lock.release()

        user_event.wait() #TODO: Time-out period?
        print("FLASK SERVER: EVENT PROCESSED...")
        event_list_lock.acquire()
        self.__remove_event_by_user_id(user_id)
        event_list_lock.release()

        msg = tcp_result
        tcp_result = "" #Empty result for security
        tcp_result_lock.release()

        return msg

    def __handle_request(self, image_bytes : bytes, complex_case: bool) -> tuple():
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
        print(f"FLASK SERVER: ACTIVE CONNECTIONS: {threading.activeCount() - 1}")
        user_id = self.__allocate_user_id()

        resized_image_base_64 = square_image(image_bytes, user_id)

        event_list_lock.acquire()
        event_list.append((user_id, threading.Event()))
        event_list_lock.release()

        print("FLASK SERVER: SENDING REQUEST TO TCP...")
        tcp_client_lock.acquire()
        tcp_client.send_request(user_id, resized_image_base_64, complex_case)
        tcp_client_lock.release()
        msg = self.__wait_for_event(user_id)


        filenames_match_temp = msg.content.split("_")
        filenames_match = []
        for item in filenames_match_temp:
            filenames_match.append(item.split("-"))
        print(filenames_match)
        with open(f"request-{user_id}.png", "wb") as f:
            f.write(msg.content)

        exif = ExifData(f"request-{user_id}.png")
        title, link, desc = ExifData.LoadData()
        os.remove(f"request-{user_id}")
        image_base64 = base64.b64encode(msg.content)
        image_base64 = image_base64.decode("ascii")

        return_msg = [
            {
                "image": image_base64,
                "title": title,
                "link": link,
                "match": 4,
                "description": desc
            }
        ]
        print(f"FLASK SERVER: USER {user_id} DONE.")
        return {"Code": 200, "Message": return_msg }, 200

#PORT MAPPINGS:
#CLIENT             -      SERVER                   :   PORT
#FLASK              -      TCP CONTROLLER           :   5050
#TCP CONTROLLER     -      IMAGE SEGMENTATION       :   5051
#TCP CONTROLLER     -      IMAGE CLASSIFICATION     :   5052
#TCP CONTROLLER     -      IMAGE COMPARER           :   5053

#ADDRESS_FLASK_TCP = (socket.gethostbyname(socket.gethostname()), 5050)

class FlaskTCPClient:
    def __init__(self, BUFFER_MAX=250000, PORT_FLASK_TCP=5050, SERVER=socket.gethostbyname(socket.gethostname()), FORMAT="ascii"):
        self.BUFFER_MAX = BUFFER_MAX
        self.PORT_FLASK_TCP = PORT_FLASK_TCP #TODO: SEE IF 
        self.SERVER = SERVER
        self.ADDRESS_FLASK_TCP = (self.SERVER, self.PORT_FLASK_TCP)
        self.FORMAT = FORMAT
        self.client_amount = 0
        self.lock = threading.Lock()

        self.client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("TCP CLIENT: STARTING...")
        print(socket.gethostbyname(socket.gethostname()))
        self.client.connect(self.ADDRESS_FLASK_TCP)

    def send_request(self, user_id: int, image_base64: base64, complex_case: bool) -> None:
        """
        Sends a `Message` object containing given variables to `self.ADRESS_FLASK_TCP`

        Variables
        ---------
        - user_id (int): Attribtute for `Message` object to be sent
        - image_base64 (base64): Attribtute for `Message` object to be sent
        - complex_cases (bool): Attribtute for `Message` object to be sent

        Returns
        ---------
        - None
        """
        print("TCP CLIENT: SENDING REQUEST...")
        self.lock.acquire()
        if self.client_amount == 0:
            thread = threading.Thread(target=self.__listen) #args=(None))
            thread.start()
        self.client_amount += 1
        self.lock.release()

        #image_base64 = base64.b64encode(image_bytes)
        image_ascii = image_base64.decode(self.FORMAT)
        msg = Message(user_id, image_ascii , complex_case, "")
        msg_json = msg.to_json()
        #CONVERT MSG TO BYTES
        converted_msg = msg_json.encode(self.FORMAT)
        print(f"TCP CLIENT: MESSAGE LENGTH: {len(converted_msg)}")
        
        #ADD PADDING TO MAKE MSG SIZE 250000
        converted_msg += b" " * (self.BUFFER_MAX - len(converted_msg))
        self.client.send(converted_msg)

    def __listen(self) -> None:
        """
        Listens on `self.ADRESS_FLASK_TCP` as long as `self.client_amount` gt 0.
        When a message is received, global `tcp_result` gets assigned to the message. After which the event storing the same `user_id` from msg gets triggered.

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

                user_id = msg_object.user_index

                tcp_result_lock.acquire()
                tcp_result = msg_object

                event_list_lock.acquire()
                user_event = get_event_by_user_id(user_id)[1]
                user_event.set()
                event_list_lock.release()
                print("done event stuff")

                self.lock.acquire()
                self.client_amount -= 1
                self.lock.release()

if __name__ == '__main__':
    tcp_client = FlaskTCPClient()
    flask_server = FlaskHTTPServer()