import socket
import threading
from Message import Message
import json
import time
import base64
import tensorflow as tf
import io
import PIL.Image as Image

class ImageSegmentationServer():
    def __init__(self, BUFFER_MAX=250000, PORT_FLASK_TCP=5051, SERVER=socket.gethostbyname(socket.gethostname()), FORMAT="ascii"):
        self.model = tf.keras.models.load_model('ImageSegmentation/model 60-40.h5')
        self.BUFFER_MAX = BUFFER_MAX
        self.FORMAT = FORMAT
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((SERVER , PORT_FLASK_TCP))
        self.connected = False

    def StartServer(self):
        print("SERVER IS STARTING...")
        self.server.listen()
        (conn, addr) = self.server.accept()
        print(f"NEW CONNECTION ESTABLISHED: {addr}")
        self.connected = True
        listenThread = threading.Thread(target=self.Listen, args=(conn,addr))
        listenThread.start()
        while self.connected:
            if listenThread.is_alive() == False:
                listenThread = threading.Thread(target=self.Listen, args=(conn,addr))
                listenThread.start()
                print(f"ACTIVE CONNECTIONS: {threading.activeCount() - 1}")
            
        self.server.close()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.SERVER , self.PORT_FLASK_TCP))
        self.StartServer()

    def Listen(self, conn, addr):
        try:
            recv_msg = conn.recv(self.BUFFER_MAX).decode(self.FORMAT)
        except:
            print("Connection to tcp server lost...")
            self.connected = False
            return

        msg_obj = Message.from_json(json.loads(recv_msg))
        print("MESSAGE RECEIVED. MESSAGE: " + str(msg_obj))
        image_ascii = msg_obj.content.encode("ascii")
        image_bytes = base64.b64decode(image_ascii)
        image = Image.open(io.BytesIO(image_bytes))
        tensor = tf.expand_dims(self.square_image(image), 0)
        pred_mask = self.model(tensor, training=False)
        new_mask = self.create_mask(pred_mask)
        new_mask = tf.keras.utils.array_to_img(new_mask)
        new_mask = new_mask.convert("RGB")
        origional_img_data = self.square_image(image).getdata()
        d = new_mask.getdata()
        newImageData = []
        for i, pixelData in enumerate(d):
            if pixelData[0] >= 250:
                newImageData.append((255, 255, 255))
            else:
                newImageData.append(origional_img_data[i])

        cutout = image
        cutout.putdata(newImageData)
        cutout.save("temp.png")
        encoded_string = ""   
        with open("temp.png", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("ascii")

        msg_obj.content = encoded_string
        msg_json = msg_obj.to_json()
        converted_msg = msg_json.encode("ascii")
        converted_msg += b" " * (self.BUFFER_MAX - len(converted_msg))
        conn.send(converted_msg)

    def create_mask(self, pred_mask):
        pred_mask = tf.argmax(pred_mask, axis=-1)
        pred_mask = pred_mask[..., tf.newaxis]
        return pred_mask[0]

    def square_image(self, image, fill_color=(255, 255, 255, 0)):
        x, y = image.size
        max_size = max(x, y)
        #create new image with size 200 x 200 and fill it with given color
        new_im = Image.new('RGB', (max_size, max_size), fill_color)
        #paste old image into the new one, y start position is 200 - x , 200 - y
        new_im.paste(image, (int((max_size - x) / 2), int((max_size - y) / 2)))
        #resize it down to 200 x 200 pixels
        resized_img = new_im.resize((128, 128))
        #save image
        #resized_img.save(image_path_name, "jpeg")
        #return resized_img
        return resized_img

if __name__ == "__main__":
    is_server = ImageSegmentationServer()
    is_server.StartServer()