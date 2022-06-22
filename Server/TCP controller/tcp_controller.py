from ast import List
from math import fabs
from multiprocessing import Queue
import socket
import threading
import json
from typing import Type
from MessageType import MessageType
from Message import Message
import time

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
    PORT_IMAGE_Comparer = 5053
    SERVER = socket.gethostbyname(socket.gethostname())
    ADDRESS_FLASK_TCP = (SERVER, PORT_FLASK_TCP)
    ADDRESS_IMAGE_SEGMENTATION = (SERVER, PORT_IMAGE_SEGMENTATION)
    ADDRESS_IMAGE_CLASSIFICATION = (SERVER, PORT_IMAGE_CLASSIFICATION)
    ADDRESS_IMAGE_COMPARER = (SERVER, PORT_IMAGE_Comparer)
    FORMAT = "ascii"
    BUFFER_SIZE = 250000
    q = Queue()
    processingUser = False
    Processed_Results = []
    segmentationClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    classificationClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    comparerClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected = False

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDRESS_FLASK_TCP)
        #print("CONNECTING TO SEGMENTATION SERVER...")
        #self.segmentationClient.connect(self.ADDRESS_IMAGE_SEGMENTATION)
        #print("CONNECTING TO CLASSIFICATION SERVER...")
        #self.classificationClient.connect(self.ADDRESS_IMAGE_CLASSIFICATION)
        #print("CONNECTING TO COMPARER SERVER...")
       # self.comparerClient.connect(self.ADDRESS_IMAGE_COMPARER)

    def StartServer(self):
        self.server.listen()
        conn, addr = self.server.accept()
        print(f"NEW CONNECTION ESTABLISHED: {addr}")
        self.connected = True
        listenThread = threading.Thread(target=self.Listen, args=(conn,addr))
        while self.connected:
            if listenThread.is_alive() == False:
                listenThread = threading.Thread(target=self.Listen, args=(conn,addr))                
                listenThread.start()
                print("Started listening...")
                print(f"ACTIVE CONNECTIONS: {threading.activeCount() - 1}")
            if self.q.qsize() > 0 and self.processingUser == False:
                if self.Processed_Results != None:
                    conn.send(self.Processed_Results.encode(self.FORMAT))
                msg_obj = self.q.get()
                #msg_obj = Message.from_json(self.q.get())
                #self.q.task_done()
                print("STARTING NN THREAD...")
                ImageSegmentationClientThread = threading.Thread(target=self.ImageSegmentationClient, args=(msg_obj,))
                ImageSegmentationClientThread.start()

        self.server.close()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDRESS_FLASK_TCP)
        self.StartServer()
            

    def Listen(self, conn, addr):
        msg = ""
        msg_obj = []
        try:
            msg = conn.recv(self.BUFFER_SIZE).decode(self.FORMAT)
            msg_obj = Message.from_json(json.loads(msg))
            print("MESSAGE RECEIVED. MESSAGE: " + msg_obj)
        except Exception as e:
            if type(e) == ConnectionResetError:
                self.connected = False

        if len(msg) > 0 and self.processingUser:
            self.q.put(msg)
        elif len(msg) > 0:
            self.processingUser = True
            print("STARTING NN THREAD...")
            ImageSegmentationClientThread = threading.Thread(target=self.ImageSegmentationClient, args=(msg_obj,))
            ImageSegmentationClientThread.start()
            

    def ImageSegmentationClient(self, msg_obj):
        converted_msg = msg_obj.to_json().encode(self.FORMAT)
        print("SENDING MESSAGE...")
        self.segmentationClient.send(converted_msg)
        new_msg_obj = Message.from_json(json.loads(self.segmentationClient.recv(self.BUFFER_SIZE).decode(self.FORMAT)))
        print("RECEIVED MESAGE FROM SEGMENTATION SERVER. MESSAGE: " + new_msg_obj)
        self.ImageClassificationClient(new_msg_obj)

    def ImageClassificationClient(self, msg_obj):
        converted_msg = msg_obj.to_json().encode(self.FORMAT)
        print("SENDING MESSAGE...")
        self.classificationClient.send(converted_msg)
        new_msg_obj = Message.from_json(json.loads(self.classificationClient.recv(self.BUFFER_SIZE).decode(self.FORMAT)))
        print("RECEIVED MESAGE FROM CLASSIFICATION SERVER. MESSAGE: " + new_msg_obj)
        if new_msg_obj.complex_case:
            self.ImageComparerClient(new_msg_obj)
            return

        if len(self.q) == 0: 
            self.processingUser = False
            self.Processed_Results = new_msg_obj
            return

        self.Processed_Results = new_msg_obj

    def ImageComparerClient(self, msg_obj):
        converted_msg = msg_obj.to_json().encode(self.FORMAT)
        print("SENDING MESSAGE...")
        self.comparerClient.send(converted_msg)
        new_msg_obj = Message.from_json(json.loads(self.comparerClient.recv(self.BUFFER_SIZE).decode(self.FORMAT)))
        print("RECEIVED MESAGE FROM COMPARER SERVER. MESSAGE: " + new_msg_obj)

        #if self.q.qsize() == 0: 
          #  self.processingUser = False
           # self.Processed_Results = new_msg_obj
          #  return

        #test = self.q.qsize()
        self.processingUser = False
        self.Processed_Results = new_msg_obj
        

if __name__ == "__main__":
    print("SERVER IS STARTING...")
    tcpController = TCPController()
    tcpController.StartServer()