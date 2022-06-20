import socket
from Message import Message

SERVER = socket.gethostbyname(socket.gethostname())

PORT = 5052
PORT_FLASK_TCP = 5050
ADDRESS_IMAGE_CLASSIFICATION = (SERVER, PORT)
ADDRESS_FLASK_TCP = (SERVER, PORT_FLASK_TCP)

FORMAT = "utf-8"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS_IMAGE_CLASSIFICATION)

conn, addr = server.accept()

msg = Message.from_json(server.recv(128).decode(FORMAT))

print(msg)


