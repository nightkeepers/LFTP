import os
import threading
from Header import *
from struct import *
import random
import sys

path = sys.path[0]
TIMEOUT = 1
SENDPATH = path+'/'
READSIZE = 2000
UNACK = 0
ACK = 1

class ClientSend(object):
    
    def __init__(self, clientSocket, serverAddress, packetNum, rwnd):
        self.window = []
        self.packets = []
        self.packets2 = []
        self.sendBase = 1
        self.packetNum = packetNum
        self.seq = 1
        self.clientSocket = clientSocket
        self.serverAddress = serverAddress
        self.rwnd = rwnd
        self.cwnd = 1
        self.ssthresh = 8

    def receive(self):
        duplicateAck = 0
        while self.sendBase <= self.packetNum:
            self.clientSocket.settimeout(TIMEOUT)
            try:
                data, _ = self.clientSocket.recvfrom(2048)
            except BaseException:
                if len(self.packets) > 0:
                    content = self.packets[0]
                    self.clientSocket.sendto(content, self.serverAddress)
                    self.ssthresh = int(self.cwnd) / 2
                    self.cwnd = 1
                    duplicateAck = 0
                else:
                    head = Header(-1, self.rwnd).getHeader()
                    content = pack('ii', head['seq'], head['rwnd'])
                    self.clientSocket.sendto(content, self.serverAddress)
                #print('TimeOut!')
            else:
                receSeq, self.rwnd = unpack('ii', data)
                #print('seq:',self.seq,' sendBase:',self.sendBase,' receSeq:',receSeq,' rwnd:',self.rwnd,' cwnd:',self.cwnd)
                #print('packets2:',self.packets2)
                if receSeq == -1:
                    pass
                elif receSeq == self.sendBase:
                    duplicateAck = 0
                    if self.cwnd >= self.ssthresh:
                        self.cwnd += 1 / self.cwnd
                    else:
                        self.cwnd += 1

                    self.window[0] = ACK
                    while len(self.window) > 0 and self.window[0] == ACK:
                        self.window.pop(0)
                        self.packets.pop(0)
                        self.packets2.pop(0)
                        self.sendBase += 1
                else:
                    self.window[receSeq - self.sendBase] = ACK
                    if duplicateAck != 3:
                        duplicateAck += 1
                        if duplicateAck == 3:
                            self.ssthresh = int(self.cwnd) / 2
                            self.cwnd = self.ssthresh + 3
                    else:
                        self.cwnd += 1

    def sendFile(self, fileName):

        thread = threading.Thread(target=self.receive)
        thread.start()
        
        fileHandler = open(SENDPATH + fileName, 'rb')
        while self.sendBase <= self.packetNum:
            if len(self.packets) < min(self.rwnd, self.cwnd) and self.seq <= self.packetNum:
                #print('rwnd:',self.rwnd,' cwnd:',self.cwnd)
                fileContent = fileHandler.read(READSIZE)
                head = Header(self.seq, self.rwnd).getHeader()
                content = pack('ii', head['seq'], head['rwnd']) + fileContent
                self.packets.append(content)
                self.window.append(UNACK)
                self.packets2.append(self.seq)
                #if random.random() > 0.01 * self.cwnd:
                self.clientSocket.sendto(content, self.serverAddress)
                self.seq += 1

        fileHandler.close()
        print('end!')