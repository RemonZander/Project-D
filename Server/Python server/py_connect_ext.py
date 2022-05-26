from flask import Flask, request
import concurrent.futures
#from flask_socketio import SocketIO
from enum import Enum
import socket
from tcp_server import *

#TODO: CREATE SERPARATE JSON FILE FOR MESSAGE TYPES FOR SERIALIZATION
class MessageType(Enum):
    SEND_IMG_FROM_EXT_TO_PY_SERVER = 1,
    SEND_IMG_FROM_PY_SERVER_TO_IMG_SEGMENTATION= 2,
    RETURN_IMG_CUTOUT_FROM_IMG_SEGMENTATION_TO_PY_SERVER = 3,
    SEND_IMG_CUT_OUT_FROM_PY_SERVER_TO_IMG_CLASSIFICATION = 4,
    RETURN_IDENTIFIED_OBJ_NAME_FROM_IMG_CLASSIFICATION_TO_PY_SERVER = 5,
    SEND_IMG_CUTOUT_AND_CATEGORY_PRODUCTS_FROM_PY_SERVER_TO_IMG_COMPARER = 6,
    RETURN_PRODUCT_LIST_FROM_IMG_COMPARER_TO_PY_SERVER = 7,
    RETURN_SEARCH_RESULTS_FROM_PY_SERVER_TO_EXT = 8,
    END_COMMUNICATION = 9,
    INIT_COMMUNICATION = 10,
    ACCEPT_COMMUNICATION = 11


app = Flask(__name__)

@app.route("/image", methods=["POST"])
def postThreads():
    if request.method == "POST":
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(image, request.files["image"])
            return future.result()

def image(uploaded_image):
    if not check_file_type(uploaded_image.filename):
        return {"errorCode": 415, "message": "The media format of the requested data is not supported by the server, so the server is rejecting the request." }, 415

    # Add functional code to process image
    
    # Change errorCode to > 200 and change message to > Image successfully uploaded
    return {"errorCode": 202, "message": "The request has been received but not yet acted upon. It is noncommittal, since there is no way in HTTP to later send an asynchronous response indicating the outcome of the request. It is intended for cases where another process or server handles the request, or for batch processing."}, 202

def check_file_type(filename):
    accepted_file_types = [".png", ".jpg", ".jpeg"]
    for type in accepted_file_types:
        if filename.endswith(type):
            return True
    return False

@app.route("/tcp", methods=["GET"])
def tcp():
    if request.method == "GET":
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 5001))
        s.send(str.encode('Hello, world'))
        data = s.recv(1024)
        s.close()
        print(repr(data))
        return f'Received: {repr(data)}'



if __name__ == '__main__':
    app.run()