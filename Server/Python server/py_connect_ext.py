from flask import Flask, request
import concurrent.futures
#from flask_socketio import SocketIO
from enum import Enum
from flask_tcp_client import *
from image_validation import *

app = Flask(__name__)

@app.route("/image", methods=["POST"])
def handle_extension_post():
    if request.method == "POST":
        #INPUT VALIDATION
        if not validate_image(request.files["image"]):
            return {"errorCode": 415, "message": "The media format of the requested data is not supported by the server, so the server is rejecting the request." }, 415

        #CREATE THREAD FOR EACH USER
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(send_request_and_poll_json)
            result = future.result()
            #TODO: Build response string
            #TODO: Return response string

def send_request_and_poll_json():
    user_id = 1 #TODO: GENERATE RANDOM USER ID
    get_search_results(user_id, request.files["image"]) #TODO: FIRE AND FORGET THIS REQUEST, CONTAINING USER I
    #TODO: Poll json file every once in a while to see if user id in file
    #TODO: If user id found, extract the results
    pass


def get_search_results(image):

    #CALL FLASK TCP CLIENT
    tcp_client.retrieve_results(image)
    pass

if __name__ == '__main__':
    tcp_client = FlaskTCPClient()
    app.run()