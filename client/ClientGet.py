import random
import Header
from struct import *
import sys

path = sys.path[0]
windowSize = 32
debug = 1


class ClientGet(object):
    def __init__(self, clientSocket):
        self.window = [0] * windowSize
        self.window2 = [-1] * windowSize
        self.rcv_base = 0
        self.packetNum = -1
        self.past = -1
        self.clientSocket = clientSocket

    def receive(self, filename):
        cnt = 0
        filehandler = open(path+"/"+filename, 'wb')
        while True:
            data, serverAddress = self.clientSocket.recvfrom(2048)
            seq = data[0:4]
            seq = unpack('i', seq)[0]
            cnt = max(cnt, seq)

            #print message
            if seq != self.past + 1:
                print("disorder packet: last packet: ", self.past, " current packet: ", seq)
            self.past = seq
            if seq % 10000 == 0 and seq != 0:
                print("has received:", seq, "packet")


            #return ack
            rwnd = windowSize - cnt + self.rcv_base - int(windowSize/5)
            head = Header.Header(seq, rwnd).getHeader()
            ack = pack('ii', head['seq'], head['rwnd'])
            self.clientSocket.sendto(ack, serverAddress)

            if seq == 0:
                self.packetNum = int(data[8:].decode("utf-8"))
                if self.packetNum == 0:
                    print("file doesn't exists")
                    break
                self.rcv_base += 1
                print("packet number:", self.packetNum)
                continue
            if seq >= self.rcv_base:
                filedata = data[8:]
                self.window[seq % windowSize] = filedata
                self.window2[seq % windowSize] = seq

            #check window and read 
            if random.random()<debug or cnt >= packetNum:
                while True:
                    if self.window2[self.rcv_base % windowSize] == self.rcv_base:
                        filehandler.write(self.window[self.rcv_base % windowSize])
                        self.rcv_base += 1
                    else:
                        break

            if self.rcv_base >= self.packetNum + 1 and self.packetNum > 0:
                break


        filehandler.close()

    



