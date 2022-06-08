from re import U
from unittest import result
from flask import Flask, request
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
event_list = []
result_list = []
index_gap_list = []
highest_user_index = -1

event_list_lock = threading.lock()
result_list_lock = threading.lock()
index_gap_list_lock = threading.lock()
highest_user_index_lock = threading.lock()
tcp_client_lock = threading.lock()

class FlaskHTTPServer():

    def __init__(self):
        self.app = Flask(__name__)
        self.app.add_url_rule("/", "image", self.handle_extension_post, methods=["POST"])

    def handle_extension_post(self):
        if request.method == "POST":
            #INPUT VALIDATION
            if not validate_image(request.files["image"]):
                return {"errorCode": 415, "message": "The media format of the requested data is not supported by the server, so the server is rejecting the request." }, 415
            #CREATE THREAD FOR EACH USER
            #thread = threading.Thread(target=self.handle_request, args=request.files["image"])
            #thread.start()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self.handle_request, request.files["image"])
                result = future.result()
                return result

    def handle_request(self, image, complex_case: bool):
        user_index = self.allocate_user_index()

        event_list_lock.acquire()
        event_list[user_index] = threading.Event()
        event_list_lock.release()

        self.send_request_to_tcp(user_index, image, complex_case)
        msg = self.wait_for_event(user_index)
        return {"Code": 200, "message": "Message succesfully processed" }, 200 #TODO: Add msg in payload

    def allocate_user_index(self) -> int:
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

        return user_index

    def deallocate_user_index(self, user_index: int) -> None:
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
        tcp_client_lock.acquire()
        tcp_client.send_request(user_index, image, complex_case)
        tcp_client_lock.release()

    def wait_for_event(self, user_index) -> None:
        event_list_lock.acquire()
        event = event_list[user_index]
        event_list_lock.release()

        event.wait() #TODO: Time-out period?

        event_list_lock.acquire()
        event_list[user_index] = None
        event_list_lock.release()

        result_list_lock.acquire()
        msg = result_list[user_index]
        result_list[user_index] = None
        result_list_lock.release()

        return msg

#PORT MAPPINGS:
#CLIENT             -      SERVER                   :   PORT
#FLASK              -      TCP CONTROLLER           :   5050
#TCP CONTROLLER     -      IMAGE SEGMENTATION       :   5051
#TCP CONTROLLER     -      IMAGE CLASSIFICATION     :   5052
#TCP CONTROLLER     -      IMAGE COMPARER           :   5053

class FlaskTCPClient:
    def __init__(self, BUFFER_MAX=128, PORT_FLASK_TCP=5050, SERVER=socket.gethostbyname(socket.gethostname()), FORMAT="utf-8"):
        self.BUFFER_MAX = BUFFER_MAX,
        self.PORT_FLASK_TCP = PORT_FLASK_TCP,
        self.SERVER = SERVER,
        self.ADDRESS_FLASK_TCP = (self.SERVER, self.PORT_FLASK_TCP),
        self.FORMAT = FORMAT
        self.client_amount = 0
        self.lock = threading.lock()

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDRESS_FLASK_TCP)

    def send_request(self, user_index: int, image, complex_case: bool) -> None:
        self.lock.acquire()
        if self.client_amount == 0:
            thread = threading.Thread(target=self.listen, args=(user_index))
            thread.start()
        self.client_amount += 1
        self.lock.release()
        
        msg = Message(user_index, image, complex_case) #TODO: Create message from image
        msg = msg.to_json()
        #CONVERT MSG TO BYTES
        converted_msg = msg.encode(self.FORMAT)
        #ADD PADDING TO MAKE MSG SIZE 128
        converted_msg += b" " * (self.BUFFER_MAX - len(converted_msg))
        self.client.send(converted_msg)

    def listen(self) -> None:
        #WAIT FOR RESPONSE
        while self.client_amount > 0:
            response = self.client.recv(self.BUFFER_MAX)
            if response:
                #TODO: Error handling, validation
                msg = response.decode(self.FORMAT)
                msg_object = Message.from_json(msg)

                user_index = msg_object.user_index

                result_list_lock.acquire()
                result_list[user_index] = msg_object
                event_list[user_index].set()
                result_list_lock.release()

                self.lock.acquire()
                self.client_amount -= 1
                self.lock.release()

if __name__ == '__main__':
    tcp_client = FlaskTCPClient()
    msg = Message(MessageType.INIT_COMM, "yeeet")
    msg = msg.to_json()
    tcp_client.send(msg)
    tcp_client = FlaskTCPClient()