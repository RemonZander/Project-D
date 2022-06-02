import concurrent.futures
from enum import Enum
import socket

class MessageType(Enum):
    SendImageFromExtensionToPyServer = 1,
    SendImageFromPyServerToImageSegmentation = 2,
    ReturnImageCutOutFromImageSegmentationToPyServer = 3,
    SendImageCutOutFromPyServerToImageClassification = 4,
    ReturnIdentifiedObjectNameFromImageClassificationToPyServer = 5,
    SendImageCutOutAndCategoryProductsFromPyServerToImageComparer = 6,
    ReturnProductListFromImageComparerToPyServer = 7,
    ReturnSearchResultsFromPyServerToExtension = 8,
    EndCommunication = 9,
    InitiateCommunication = 10,
    AcceptCommunication = 11

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", 5001))
    s.listen(1)
    conn, addr = s.accept()
    while 1:
        data = conn.recv(1024)
        if not data:
            break
        print(repr(data))
        conn.sendall(data)
    conn.close()
        


if __name__ == '__main__':
    main()