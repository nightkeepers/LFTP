import os
import threading
from Header import *
from struct import *

TIMEOUT = 3
WINDOW_SIZE = 10
PATH = 'data/'
UNACK = 0
ACK = 1
window = []
packets = []
sendBase = 0
packetNum = 0

def getFile(serverSocket, fileName, clientAddress, packetNum, port, p):
    filehandler = open(PATH + fileName, 'wb')
    packetNum = int(packetNum)
    for i in range(packetNum):
        serverSocket.settimeout(TIMEOUT)
        try:
            data, clientAddress = serverSocket.recvfrom(2048)
        except BaseException as e:
            print(e)
        else:
            # write the data to the file
            filehandler.write(data)

    # close the file
    filehandler.close()
    port.append(p)