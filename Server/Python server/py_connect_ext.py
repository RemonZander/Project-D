from flask import Flask, request
import concurrent.futures
from flask_socketio import SocketIO
from enum import Enum

class MessageType(Enum):
    SendImageFromExtensionToPyServer = 1,
    SendImageFromPyServerToImageSegmentation = 2,
    ReturnImageCutOutFromImageSegmentationToPyServer = 3,
    SendImageCutOutFromPyServerToImageClassification = 4,
    ReturnIdentifiedObjectNameFromImageClassificationToPyServer = 5,
    SendImageCutOutAndCategoryProductsFromPyServerToImageComparer = 6,
    ReturnProductListFromImageComparerToPyServer = 7,
    ReturnSearchResultsFromPyServerToExtension = 8,
    EndCommunication = 9,
    InitiateCommunication = 10,
    AcceptCommunication = 11


app = Flask(__name__)

socketio = SocketIO(app)

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

@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))

if __name__ == '__main__':
    socketio.run(app)