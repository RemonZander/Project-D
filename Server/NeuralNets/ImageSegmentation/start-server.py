import socket

FORMAT = "utf-8"
PORT = 5051

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(PORT)

conn, addr = server.accept()

msg = conn.recv(128).decode(FORMAT)
