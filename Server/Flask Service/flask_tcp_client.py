import socket
import threading
import json
from MessageType import MessageType
from Message import Message
import time

#PORT MAPPINGS:
#CLIENT             -      SERVER                   :   PORT
#FLASK              -      TCP CONTROLLER           :   5050
#TCP CONTROLLER     -      IMAGE SEGMENTATION       :   5051
#TCP CONTROLLER     -      IMAGE CLASSIFICATION     :   5052
#TCP CONTROLLER     -      IMAGE COMPARER           :   5053

class FlaskTCPClient:
    def __init__(self, BUFFER_MAX=128, PORT_FLASK_TCP=5050, SERVER=socket.gethostbyname(socket.gethostname()), FORMAT="ascii"):
        self.BUFFER_MAX = BUFFER_MAX,
        self.PORT_FLASK_TCP = PORT_FLASK_TCP,
        self.SERVER = SERVER,
        self.ADDRESS_FLASK_TCP = (self.SERVER, self.PORT_FLASK_TCP),
        self.FORMAT = FORMAT

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDRESS_FLASK_TCP)
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

if __name__ == "__main__":
    tcp_client = FlaskTCPClient()
    msg = Message(MessageType.INIT_COMM, "yeeet")
    msg = msg.to_json()
    tcp_client.send(msg)
    time.sleep(2)
    msg = Message(MessageType.INIT_COMM, "yeeet2")
    msg = msg.to_json()
    tcp_client.send(msg)