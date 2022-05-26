import socket
import threading
import json
from MessageType import MessageType
from Message import Message

HEADER_MAX = 128 #TODO: CHECK IF THIS SIZE IS SUITABLE FOR THIS PROJECT
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDRESS)

def send(msg : str):
    #CONVERT MSG TO BYTES
    converted_msg = msg.encode(FORMAT)
    #GET BYTE LENGTH OF MSG AND SAVE IN STRING
    msg_length = str(len(converted_msg))
    #CREATE INIT MESSAGE OBJECT TO SEND
    init_msg = Message(MessageType.HEADER, msg_length)
    #SERIALIZE TO JSON
    init_msg = init_msg.to_json()
    #SERIALZE TO BYTE
    converted_init_msg = init_msg.encode(FORMAT)

    #ADD PADDING TO MAKE MSG SIZE 128
    converted_init_msg += b" " * (HEADER_MAX - len(converted_init_msg))

    client.send(converted_init_msg)
    #NOW SEND ACTUAL MESSAGE
    client.send(converted_msg)

if __name__ == "__main__":
    msg = Message(MessageType.INIT_COMM, "yeeet")
    msg = msg.to_json()
    send(msg)