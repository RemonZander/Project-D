from flask import Flask, request

app = Flask(__name__)

@app.route("/image", methods=["POST"])
def image():
    if request.method == "POST":
        uploaded_image = request.files["image"]

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

if __name__ == '__main__':
    app.run()