from ast import List
from math import fabs
from multiprocessing import Queue
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


class TCPController():
    PORT_FLASK_TCP = 5050
    PORT_IMAGE_SEGMENTATION = 5051
    PORT_IMAGE_CLASSIFICATION = 5052
    PORT_IMAGE_Comparer = 5053
    SERVER_ADDRESS = socket.gethostbyname(socket.gethostname())
    ADDRESS_FLASK_TCP = (SERVER_ADDRESS, PORT_FLASK_TCP)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ADDRESS_IMAGE_SEGMENTATION = (SERVER_ADDRESS, PORT_IMAGE_SEGMENTATION)
    ADDRESS_IMAGE_CLASSIFICATION = (SERVER_ADDRESS, PORT_IMAGE_CLASSIFICATION)
    ADDRESS_IMAGE_COMPARER = (SERVER_ADDRESS, PORT_IMAGE_Comparer)
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
        self.server.bind(self.ADDRESS_FLASK_TCP)
        print("CONNECTING TO SEGMENTATION SERVER...")
        try:
            self.segmentationClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.segmentationClient.connect(self.ADDRESS_IMAGE_SEGMENTATION)
        except:
            print("Can't connect to segmentation server. Will try later again")
        print("CONNECTING TO CLASSIFICATION SERVER...")
        try:
            self.classificationClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.classificationClient.connect(self.ADDRESS_IMAGE_CLASSIFICATION)
        except:
             print("Can't connect to classification server. Will try later again")
        print("CONNECTING TO COMPARER SERVER...")
        try:
            self.comparerClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.comparerClient.connect(self.ADDRESS_IMAGE_COMPARER)
        except:
            print("Can't connect to comparer server. Will try later again")

    def StartServer(self):
        print("SERVER IS STARTING...")
        self.server.listen()
        (conn, addr) = self.server.accept()
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
            if self.q.qsize() > 0 and self.processingUser == False:
                msg_obj = self.q.get()
                print("STARTING NN THREAD...")
                ImageSegmentationClientThread = threading.Thread(target=self.ImageSegmentationClient, args=(msg_obj,))
                ImageSegmentationClientThread.start()
            if self.Processed_Results != [] and self.processingUser == False:
                msg = self.Processed_Results.to_json().encode(self.FORMAT)
                msg += b" " * (self.BUFFER_SIZE - len(msg))
                conn.send(msg)

        self.server.close()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__init__()
        self.StartServer()
            

    def Listen(self, conn, addr):
        msg = ""
        msg_obj = []
        try:
            print("Started listening...")
            msg = conn.recv(self.BUFFER_SIZE).decode(self.FORMAT)
            print("MESSAGE RECEIVED. MESSAGE: " + msg)
            msg_obj = Message.from_json(json.loads(msg))
        except Exception as e:
            if type(e) == ConnectionResetError:
                self.connected = False
                print("Restarting server...")
            else:
                print("Error with msg_obj")
                print(e)

        if len(msg) > 0 and self.processingUser:
            self.q.put(msg)
        elif len(msg) > 0:
            self.processingUser = True
            print("STARTING NN THREAD...")
            ImageSegmentationClientThread = threading.Thread(target=self.ImageSegmentationClient, args=(msg_obj,))
            ImageSegmentationClientThread.start()
            

    def ImageSegmentationClient(self, msg_obj):
        converted_msg = msg_obj.to_json().encode(self.FORMAT)
        print("SENDING MESSAGE TO SEGMENTATION...")
        try:
            self.segmentationClient.send(converted_msg)
        except:
            print("reconnecting to segmentation server...")
            try:
                self.segmentationClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.segmentationClient.connect(self.ADDRESS_IMAGE_SEGMENTATION)
                print("SENDING MESSAGE...")
                self.segmentationClient.send(converted_msg)
            except:
                print("can't connect to segmentation server. Will try in 1 second again")
                time.sleep(1)
                self.ImageSegmentationClient(msg_obj)
        try:
            new_msg_obj = Message.from_json(json.loads(self.segmentationClient.recv(self.BUFFER_SIZE).decode(self.FORMAT)))
        except:
            print("Lost connection to segmentation server")
            print("reconnecting to segmentation server...")
            try:
                self.segmentationClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.segmentationClient.connect(self.ADDRESS_IMAGE_SEGMENTATION)
                print("SENDING MESSAGE...")
                self.segmentationClient.send(converted_msg)
            except:
                print("can't connect to segmentation server. Will try in 1 second again")
                time.sleep(1)
                self.ImageSegmentationClient(msg_obj)
        print("RECEIVED MESAGE FROM SEGMENTATION SERVER. MESSAGE: " + str(new_msg_obj))
        self.ImageClassificationClient(new_msg_obj)

    def ImageClassificationClient(self, msg_obj):
        converted_msg = msg_obj.to_json().encode(self.FORMAT)
        print("SENDING MESSAGE...")
        try:
            self.classificationClient.send(converted_msg)
        except:
            print("reconnecting to classification server...")
            try:
                self.classificationClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.classificationClient.connect(self.ADDRESS_IMAGE_CLASSIFICATION)
                print("SENDING MESSAGE...")
                self.classificationClient.send(converted_msg)
            except:
                print("can't connect to classification server. Will try in 1 second again")
                time.sleep(1)
                self.ImageClassificationClient(msg_obj)
        try:
            new_msg_obj = Message.from_json(json.loads(self.classificationClient.recv(self.BUFFER_SIZE).decode(self.FORMAT)))
        except:
            print("Lost connection to classification server")
            print("reconnecting to classification server...")
            try:
                self.classificationClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.classificationClient.connect(self.ADDRESS_IMAGE_CLASSIFICATION)
                print("SENDING MESSAGE...")
                self.classificationClient.send(converted_msg)
            except:
                print("can't connect to classification server. Will try in 1 second again")
                time.sleep(1)
                self.ImageClassificationClient(msg_obj)
        print("RECEIVED MESAGE FROM CLASSIFICATION SERVER. MESSAGE: " + str(new_msg_obj))
        if new_msg_obj.complex_case:
            self.ImageComparerClient(new_msg_obj)
            return

        #if len(self.q) == 0: 
        #    self.processingUser = False
        #    self.Processed_Results = new_msg_obj
         #   return

        self.processingUser = False
        self.Processed_Results = new_msg_obj

    def ImageComparerClient(self, msg_obj):
        converted_msg = msg_obj.to_json().encode(self.FORMAT)
        jsonvoorbeeld = msg_obj.to_json()
        new_msg_obj = []
        print("SENDING MESSAGE...")
        try:
            self.comparerClient.send(converted_msg)
        except:
            print("reconnecting to classification server...")
            try:
                self.comparerClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.comparerClient.connect(self.ADDRESS_IMAGE_COMPARER)
                print("SENDING MESSAGE...")
                self.comparerClient.send(converted_msg)
            except:
                print("can't connect to comparer server. Will try in 1 second again")
                time.sleep(1)
                self.ImageComparerClient(msg_obj)
        try:
            msg = self.comparerClient.recv(self.BUFFER_SIZE).decode(self.FORMAT)
            msg = msg[0:msg.rfind('}') + 1]
            new_msg_obj = Message.from_json(json.loads(msg))
        except:
            print("Lost connection to comparer server")
            print("reconnecting to comparer server...")
            try:
                self.comparerClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.comparerClient.connect(self.ADDRESS_IMAGE_COMPARER)
                print("SENDING MESSAGE...")
                self.comparerClient.send(converted_msg)
            except:
                print("can't connect to comparer server. Will try in 1 second again")
                time.sleep(1)
                self.ImageClassificationClient(msg_obj)
        print("RECEIVED MESAGE FROM COMPARER SERVER. MESSAGE: " + str(new_msg_obj))

        #if self.q.qsize() == 0: 
          #  self.processingUser = False
           # self.Processed_Results = new_msg_obj
          #  return

        #test = self.q.qsize()
        self.processingUser = False
        self.Processed_Results = new_msg_obj
        

if __name__ == "__main__":
    tcpController = TCPController()
    tcpController.StartServer()