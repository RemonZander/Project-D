import socket
import threading
from Message import Message
import json
import time
import random
import base64

class DummyServer():
    def __init__(self, BUFFER_MAX=250000, PORT_FLASK_TCP=5050, SERVER=socket.gethostbyname(socket.gethostname()), FORMAT="utf-8"):
        self.BUFFER_MAX = BUFFER_MAX
        self.FORMAT = FORMAT
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("DUMMY SERVER: STARTING...")
        self.server.bind((SERVER , PORT_FLASK_TCP))

    def listen(self):
        self.server.listen()
        while True:
            #WHEN NEW CONNECTION, STORE ADDRESS TUPLE IN "addr" AND THE CONNECTION OBJECT IN "conn"
            (conn, addr) = self.server.accept()

            #CREATE NEW THREAD TO HANDLE CONNECTION
            thread = threading.Thread(target=self.handle_client, args=(conn,addr))
            thread.start()
            print(f"DUMMY SERVER: ACTIVE CONNECTIONS: {threading.activeCount() - 1}")

    def handle_client(self, conn, addr):
        print(f"DUMMY SERVER: NEW CONNECTION ESTABLISHED: {addr}")
        connected = True
        while connected:
            recv_msg = conn.recv(self.BUFFER_MAX)#.decode("ascii")
            if recv_msg:
                print(f"DUMMY SERVER: MESSAGE RECEIVED: {recv_msg}")

                msg_str = recv_msg.decode("ascii")
                msg_dict = json.loads(msg_str)
                msg_obj = Message.from_json(msg_dict)

                user_index = msg_obj.user_index
                complex_case = msg_obj.complex_case
                image_attr = msg_obj.content.encode("ascii")

                image_base64 = base64.b64decode(image_attr)
                with open ("testimage.jpg", "wb") as b:
                    print("writing")
                    b.write(image_base64)
                    print("Written")

                resp_msg = Message(user_index, "RESPONSE MESSAGE!", complex_case)
                msg_str = resp_msg.to_json()
                msg_bytes = msg_str.encode(self.FORMAT)
                time.sleep(float(random.randint(2,3)))
                conn.send(msg_bytes)

if __name__ == "__main__":
    dummy_server = DummyServer()
    dummy_server.listen()