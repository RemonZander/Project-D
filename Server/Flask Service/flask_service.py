from flask import Flask, request
import concurrent.futures
#from flask_socketio import SocketIO
from enum import Enum
from flask_tcp_client import *
from image_validation import *
import threading

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


event_list = []
result_list = []
index_gap_list = []
highest_user_id = -1

app = Flask(__name__)

@app.route("/image", methods=["POST"])
def handle_extension_post():
    if request.method == "POST":
        #INPUT VALIDATION
        if not validate_image(request.files["image"]):
            return {"errorCode": 415, "message": "The media format of the requested data is not supported by the server, so the server is rejecting the request." }, 415

        #CREATE THREAD FOR EACH USER
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(handle_request, request.files["image"])
            result = future.result()
            #TODO: Build response string
            #TODO: Return response string

def handle_request(image):
    user_id = allocate_user_id()
    get_search_results(user_id, image) #TODO: FIRE AND FORGET THIS REQUEST, CONTAINING USER I

def allocate_user_id() -> int:
    global highest_user_id
    global index_gap_list
    user_id = -1
    #Lock thread
    if len(index_gap_list) > 0:
        user_id = index_gap_list[0]
        index_gap_list.remove(index_gap_list[0])
    else:
        user_id = highest_user_id + 1
        highest_user_id = user_id
    #Unlock thread
    return user_id

def deallocate_user_id(user_id: int) -> None:
    global highest_user_id
    global index_gap_list
    #Lock thread
    if user_id == highest_user_id:
        for item in event_list[::-1]:
            pass
    #Unlock thread

def wait_for_event(event) -> None:
    # make the thread wait for event
    event_set = event.wait()
    if event_set:
      print("Event received, releasing thread...")
    else:
     print("Time out, moving ahead without event...")

def get_search_results(image):
    #CALL FLASK TCP CLIENT
    tcp_client.retrieve_results(image)
    pass

import socket
import threading
import json
from MessageType import MessageType
from Message import Message

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

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDRESS)
        self.user_list = []

    def retrieve_results(self, user_id, image):
        if len(self.user_list) == 0:
            #Create receiver thread
            pass
        
        self.user_list.append(user_id)


        #TODO: VALIDATE IMAGE

        #CREATE MESSAGE OBJECTS
        #SEND MESSAGE
        #RETURN RESULTS
        pass

    def __send(self, msg : str):
        #CONVERT MSG TO BYTES
        converted_msg = msg.encode(self.FORMAT)
        #GET BYTE LENGTH OF MSG AND SAVE IN STRING
        msg_length = str(len(converted_msg))
        #CREATE INIT MESSAGE OBJECT TO SEND
        init_msg = Message(MessageType.HEADER, msg_length)
        #SERIALIZE TO JSON
        init_msg = init_msg.to_json()
        #SERIALZE TO BYTE
        converted_init_msg = init_msg.encode(self.FORMAT)

        #ADD PADDING TO MAKE MSG SIZE 128
        converted_init_msg += b" " * (self.BUFFER_MAX - len(converted_init_msg))

        self.client.send(converted_init_msg)
        #NOW SEND ACTUAL MESSAGE
        self.client.send(converted_msg)

        #WAIT FOR RESPONSE
        while True:
            response = self.client.recv(self.BUFFER_MAX)
            if response:
                pass

if __name__ == '__main__':
    tcp_client = FlaskTCPClient()
    msg = Message(MessageType.INIT_COMM, "yeeet")
    msg = msg.to_json()
    tcp_client.send(msg)
    tcp_client = FlaskTCPClient()
    app.run()

