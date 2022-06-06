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
    SERVER = socket.gethostbyname(socket.gethostname())
    ADDRESS_FLASK_TCP = (SERVER, PORT_FLASK_TCP)
    ADDRESS_IMAGE_SEGMENTATION = (SERVER, PORT_IMAGE_SEGMENTATION)
    FORMAT = "utf-8"
    q = Queue()

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDRESS_FLASK_TCP)

    def StartServer(self):
        conn, addr = self.server.accept()
        print(f"NEW CONNECTION ESTABLISHED: {addr}")
        connected = True
        thread = threading.Thread(target=self.Listen, args=(conn,addr))
        while connected:
            if thread.is_alive() != True:
                thread.start()
                print(f"ACTIVE CONNECTIONS: {threading.activeCount() - 1}")
            msg_obj = Message.from_json(self.q.get())
            self.q.task_done()
            

    def Listen(self, conn, addr):
        self.q.put(conn.recv(128).decode(self.FORMAT))

    def ImageSegmentationClient(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDRESS_IMAGE_SEGMENTATION)
        


if __name__ == "__main__":
    print("SERVER IS STARTING...")
    tcpController = TCPController()
    tcpController.StartServer()