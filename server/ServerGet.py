import os
import threading
from Header import *
from struct import *

WINDOW_SIZE = 32
PATH = 'data2/'

class ServerGet(object):
    def __init__(self, serverSocket, clientAddress, packetNum):
        self.window = [0] * WINDOW_SIZE
        self.window2 = [-1] * WINDOW_SIZE
        self.rcv_base = 1
        self.serverSocket = serverSocket
        self.clientAddress = clientAddress
        self.packetNum = packetNum

    def getFile(self, fileName, port, p):
        filehandler = open(PATH + fileName, 'wb')
        cnt = 1
        seq = 0
        head = Header(seq, WINDOW_SIZE - cnt + self.rcv_base - int(WINDOW_SIZE / 5)).getHeader()
        self.serverSocket.sendto(pack('ii', head['seq'], head['rwnd']), self.clientAddress)
        while True:
            data, _ = self.serverSocket.recvfrom(2048)
            seq = unpack('i', data[0:4])[0]
            cnt = max(cnt, seq)

            #return ack
            head = Header(seq, WINDOW_SIZE - cnt + self.rcv_base - int(WINDOW_SIZE / 5)).getHeader()
            ack = pack('ii', head['seq'], head['rwnd'])
            self.serverSocket.sendto(ack, self.clientAddress)

            if seq >= self.rcv_base:
                filedata = data[8:]
                self.window[seq % WINDOW_SIZE] = filedata
                self.window2[seq % WINDOW_SIZE] = seq

            #check window and read            
            while True:
                if self.window2[self.rcv_base % WINDOW_SIZE] == self.rcv_base:
                    filehandler.write(self.window[self.rcv_base % WINDOW_SIZE])
                    self.rcv_base += 1
                else:
                    break

            if self.rcv_base >= self.packetNum + 1 and self.packetNum > 0:
                break

        # close the file
        filehandler.close()
        port.append(p)
        self.serverSocket.close()
        print(self.clientAddress, ' upload end!')