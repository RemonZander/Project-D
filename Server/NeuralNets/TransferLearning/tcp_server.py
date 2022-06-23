import socket
import threading
from Message import Message
import json
import time
import base64
import tensorflow as tf
import io
import PIL.Image as Image
import numpy as np

class ImageClassificationServer():
    def __init__(self, BUFFER_MAX=250000, PORT_FLASK_TCP=5052, SERVER=socket.gethostbyname(socket.gethostname()), FORMAT="utf-8"):
        self.model = tf.keras.models.load_model('TransferLearning/TransferlearningModel.h5')
        self.BUFFER_MAX = BUFFER_MAX
        self.FORMAT = FORMAT
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((SERVER , PORT_FLASK_TCP))
        self.connected = False
        self.class_names = [
            "jassen",
            "lange broeken",
            "korte broeken",
            "slippers",
            "sneakers",
            "t-shirts",
        ]

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
        predictions = self.model(tensor, training=False)
        predicted_class = self.class_names[np.argmax(tf.nn.softmax(predictions[0]))]
        msg_obj.class_name = predicted_class
        msg_json = msg_obj.to_json()
        converted_msg = msg_json.encode("ascii")
        converted_msg += b" " * (self.BUFFER_MAX - len(converted_msg))
        conn.send(converted_msg)
        

    def square_image(self, image, fill_color=(255, 255, 255, 0)):
        x, y = image.size
        max_size = max(x, y)
        new_im = Image.new('RGB', (max_size, max_size), fill_color)
        new_im.paste(image, (int((max_size - x) / 2), int((max_size - y) / 2)))
        resized_img = new_im.resize((160, 160))
        return resized_img

if __name__ == "__main__":
    ic_server = ImageClassificationServer()
    ic_server.StartServer()