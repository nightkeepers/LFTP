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
        self.rcv_base = 0
        self.seq = 0
        self.serverSocket = serverSocket
        self.clientAddress = clientAddress
        self.packetNum = packetNum

    def getFile(self, fileName, port, p):
        filehandler = open(PATH + fileName, 'wb')
        cnt = 0
        head = Header(self.seq, WINDOW_SIZE - cnt + self.rcv_base - int(WINDOW_SIZE / 5)).getHeader()
        self.serverSocket.sendto(pack('ii', head['seq'], head['rwnd']), self.clientAddress)
        self.seq += 1
        while True:
            data, _ = self.serverSocket.recvfrom(2048)
            self.seq = unpack('i', data[0:4])[0]
            cnt = max(cnt, self.seq)

            #return ack
            head = Header(self.seq, WINDOW_SIZE - cnt + self.rcv_base - int(WINDOW_SIZE / 5)).getHeader()
            ack = pack('ii', head['seq'], head['rwnd'])
            self.serverSocket.sendto(ack, self.clientAddress)
            if self.seq == 0:
                packetNum = int(data[8:].decode("utf-8"))
                if packetNum == 0:
                    print("file doesn't exists")
                    break
                self.rcv_base += 1
                print(packetNum)
                continue
            if self.seq >= self.rcv_base:
                filedata = data[8:]
                self.window[self.seq % WINDOW_SIZE] = filedata
                self.window2[self.seq % WINDOW_SIZE] = self.seq

            #check window and read            
            while True:
                if self.window2[self.rcv_base % WINDOW_SIZE] == self.rcv_base:
                    filehandler.write(self.window[self.rcv_base % WINDOW_SIZE])
                    self.rcv_base += 1
                else:
                    break

            if self.rcv_base >= packetNum + 1 and packetNum > 0:
                break

        # close the file
        filehandler.close()
        port.append(p)
        self.serverSocket.close()