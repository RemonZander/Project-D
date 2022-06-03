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
available_indexes = []
highest_user_id = -1

app = Flask(__name__)

@app.route("/image", methods=["POST"])
def handle_extension_post():
    if request.method == "POST":
        #INPUT VALIDATION
        if not validate_image(request.files["image"]):
            return {"errorCode": 415, "message": "The media format of the requested data is not supported by the server, so the server is rejecting the request." }, 415

        #generate user id

        #CREATE THREAD FOR EACH USER
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(send_request, request.files["image"])
            result = future.result()
            #TODO: Build response string
            #TODO: Return response string

        #remove user id


def send_request(image):
    user_id = allocate_user_id()
    get_search_results(user_id, image) #TODO: FIRE AND FORGET THIS REQUEST, CONTAINING USER I

def allocate_user_id() -> int:
    global highest_user_id
    global available_indexes
    #Lock thread
    user_id = -1
    if len(available_indexes) > 0:
        user_id = available_indexes[0]
        available_indexes.remove(available_indexes[0])
    else:
        user_id = highest_user_id + 1
        highest_user_id = user_id
    return user_id

def deallocate_user_id(user_id: int) -> None:
    global highest_user_id
    global available_indexes

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

if __name__ == '__main__':
    tcp_client = FlaskTCPClient()
    app.run()