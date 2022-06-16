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

def search_event_by_user_index(user_index) -> threading.Event:
    global event_list
    for event in event_list:
        if event[0] == user_index:
            return event[1]

def remove_event_by_user_index(user_index) -> threading.Event:
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
        self.app.add_url_rule("/test", "test", self.test_handle, methods=["GET"])
        self.app.run(debug=True)

    def handle_extension_post(self):
        if request.method == "POST":
            print("FLASK SERVER: NEW CLIENT CONNECTING...")
            #INPUT VALIDATION

            image = request.files["image"]
            if not validate_image(image):
                return {"errorCode": 415, "message": "The media format of the requested data is not supported by the server, so the server is rejecting the request." }, 415

            #CREATE THREAD FOR EACH USER
            #thread = threading.Thread(target=self.handle_request, args=request.files["image"])
            #thread.start()

            complex_case = request.form["complex_case"]
            print(f"IMAGE TYPE: {type(image)}")

            #with concurrent.futures.ThreadPoolExecutor() as executor:
                #future = executor.submit(self.handle_request, request.files["image"])
               #result = future.result()
                #return result

            #return self.handle_request(image, complex_case)
            return "yeet"

    def test_handle(self):
        if request.method == "GET":
            return "Get"

    def debug_func(self):
        #with concurrent.futures.ThreadPoolExecutor() as executor:
            #executor.submit(self.handle_request, "payload", True)

        thread = threading.Thread(target=self.handle_request, args=("payload", True))
        thread.start()

    def handle_request(self, image, complex_case: bool):
        print("FLASK SERVER: HANDLING REQUEST...")
        print(f"FLASK SERVER: ACTIVE CONNECTIONS: {threading.activeCount() - 1}")
        user_index = self.allocate_user_index()

        event_list_lock.acquire()
        event_list.append((user_index, threading.Event()))
        event_list_lock.release()

        self.send_request_to_tcp(user_index, image, complex_case)
        msg = self.wait_for_event(user_index)
        self.deallocate_user_index(user_index)
        print(f"FLASK SERVER: USER {user_index} DONE.")
        return {"Code": 200, "message": "Message succesfully processed" }, 200 #TODO: Add msg in payload

    def allocate_user_index(self) -> int:
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
        else:
            index_gap_list.append(user_index)

        highest_user_index_lock.release()
        event_list_lock.release()
        index_gap_list_lock.release()

    def send_request_to_tcp(self, user_index, image, complex_case):
        print("FLASK SERVER: SENDING REQUEST TO TCP...")
        tcp_client_lock.acquire()
        tcp_client.send_request(user_index, image, complex_case)
        tcp_client_lock.release()

    def wait_for_event(self, user_index) -> None:
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
    def __init__(self, BUFFER_MAX=128, PORT_FLASK_TCP=5050, SERVER=socket.gethostbyname(socket.gethostname()), FORMAT="utf-8"):
        self.BUFFER_MAX = BUFFER_MAX
        self.PORT_FLASK_TCP = PORT_FLASK_TCP #TODO: SEE IF 
        self.SERVER = SERVER
        self.ADDRESS_FLASK_TCP = (self.SERVER, self.PORT_FLASK_TCP)
        self.FORMAT = FORMAT
        self.client_amount = 0
        self.lock = threading.Lock()

        self.client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_tcp_client(self) -> None:
        print("TCP CLIENT: STARTING...")
        print(socket.gethostbyname(socket.gethostname()))
        self.client.connect(self.ADDRESS_FLASK_TCP)

        print("TCP CLIENT: SENDING REQUEST...")
        converted_msg = "your mom".encode(self.FORMAT)
        converted_msg += b" " * (self.BUFFER_MAX - len(converted_msg))
        self.client.send(converted_msg)
        time.sleep(2)
        converted_msg = "your mom".encode(self.FORMAT)
        converted_msg += b" " * (self.BUFFER_MAX - len(converted_msg))
        self.client.send(converted_msg)

    def send_request(self, user_index: int, image, complex_case: bool) -> None:
        print("TCP CLIENT: SENDING REQUEST...")
        self.lock.acquire()
        if self.client_amount == 0:
            thread = threading.Thread(target=self.listen) #args=(None))
            thread.start()
        self.client_amount += 1
        self.lock.release()

        msg = Message(user_index, image, complex_case) #TODO: Create message from image
        msg = msg.to_json()
        #CONVERT MSG TO BYTES
        converted_msg = msg.encode(self.FORMAT)
        print(f"TCP CLIENT: MESSAGE LENGTH: {len(converted_msg)}")
        #ADD PADDING TO MAKE MSG SIZE 128
        converted_msg += b" " * (self.BUFFER_MAX - len(converted_msg))
        self.client.send(converted_msg)

    def listen(self) -> None:
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