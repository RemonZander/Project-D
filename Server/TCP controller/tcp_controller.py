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


HEADER_MAX = 128 #TODO: CHECK IF THIS SIZE IS SUITABLE FOR THIS PROJECT
PORT_FLASK_TCP = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDRESS_FLASK_TCP = (SERVER, PORT_FLASK_TCP)
FORMAT = "utf-8"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS_FLASK_TCP)

def handle_client(conn, addr):
    print(f"NEW CONNECTION ESTABLISHED: {addr}")
    connected = True
    while connected:
        #INITIAL MSG FROM ClIENT MUST BE OF TYPE "HEADER" AND CONTAIN LENGTH OF ACTUAL MSG
        init_msg = conn.recv(HEADER_MAX).decode(FORMAT)
        if init_msg:
            print(f"MESSAGE {init_msg}")
            #DESERIALIZE FROM STR TO "Message" OBJ
            init_msg = json.loads(init_msg)
            msg_obj = Message.from_json(init_msg)
            if msg_obj.type != MessageType.HEADER:
                #TODO: NOT VALID INPUT - ADD ERROR HANDLING
                pass
            msg_len = int(msg_obj.content)
            print(f"msg len: {msg_len}")
            #NOW WAIT FOR CONTENT WITH THE DEFINED LENGTH
            msg = conn.recv(msg_len).decode(FORMAT)
            #ACTUAL MESSAGE
            print("MESSAGE RECEIVED: " + msg)

           #TODO: IF SWITCHES (OR MATCH CASE IF PYTHON 3.10) FOR DIFFERENT MESSAGE TYPES

    conn.close()

def start():
    server.listen()
    while True:
        #WHEN NEW CONNECTION, STORE ADDRESS TUPLE IN "addr" AND THE CONNECTION OBJECT IN "conn"
        conn, addr = server.accept()

        #CREATE NEW THREAD TO HANDLE CONNECTION
        thread = threading.Thread(target=handle_client, args=(conn,addr))
        thread.start()
        print(f"ACTIVE CONNECTIONS: {threading.activeCount() - 1}")


if __name__ == "__main__":
    print("SERVER IS STARTING...")
    start()