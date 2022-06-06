from multiprocessing import Queue
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


class TCPController():
    PORT_FLASK_TCP = 5050
    PORT_IMAGE_SEGMENTATION = 5051
    PORT_IMAGE_CLASSIFICATION = 5052
    SERVER = socket.gethostbyname(socket.gethostname())
    ADDRESS_FLASK_TCP = (SERVER, PORT_FLASK_TCP)
    ADDRESS_IMAGE_SEGMENTATION = (SERVER, PORT_IMAGE_SEGMENTATION)
    ADDRESS_IMAGE_CLASSIFICATION = (SERVER, PORT_IMAGE_CLASSIFICATION)
    FORMAT = "utf-8"
    q = Queue()
    processingUser = False

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDRESS_FLASK_TCP)

    def StartServer(self):
        conn, addr = self.server.accept()
        print(f"NEW CONNECTION ESTABLISHED: {addr}")
        connected = True
        listenThread = threading.Thread(target=self.Listen, args=(conn,addr))       
        while connected:
            if listenThread.is_alive() != True:
                listenThread.start()
                print(f"ACTIVE CONNECTIONS: {threading.activeCount() - 1}")
            if len(self.q) > 0:
                msg_obj = Message.from_json(self.q.get())
                self.q.task_done()
                ImageSegmentationClientThread = threading.Thread(target=self.ImageSegmentationClient, args=(msg_obj))
                ImageSegmentationClientThread.start()
                #if len(self.q) == 0: self.processingUser = False
            

    def Listen(self, conn, addr):
        msg = conn.recv(128).decode(self.FORMAT)
        if len(msg) > 0 and self.processingUser:
            self.q.put(msg)
        elif len(msg) > 0:
            self.processingUser = True
            ImageSegmentationClientThread = threading.Thread(target=self.ImageSegmentationClient, args=(msg))
            ImageSegmentationClientThread.start()
            

    def ImageSegmentationClient(self, msg):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(self.ADDRESS_IMAGE_SEGMENTATION)
        converted_msg = msg.encode(self.FORMAT)
        #msg_length = str(len(converted_msg))
        client.send(converted_msg)
        msg = client.recv(128).decode(self.FORMAT)
        self.ImageClassificationClient(msg)

    def ImageClassificationClient(self, msg):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(self.ADDRESS_IMAGE_SEGMENTATION)
        converted_msg = msg.encode(self.FORMAT)
        client.send(converted_msg)
        msg = Message.from_json(client.recv(128).decode(self.FORMAT))
        
        

if __name__ == "__main__":
    print("SERVER IS STARTING...")
    tcpController = TCPController()
    tcpController.StartServer()