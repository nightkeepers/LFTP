from socket import *
import sys
import os
import hashlib
import Header
from struct import *
import random

path = sys.path[0]

#serverName = "2001:250:3002:4251:acb9:7567:3619:ad1b"
serverName = "172.18.33.0"
serverPort = 6666
UDPSocket = socket(AF_INET, SOCK_DGRAM)
#UDPSocket = socket(AF_INET6, SOCK_DGRAM)
UDPSocket.bind(("", 6666))
windowSize = 32
debug = 1
window = [0] * windowSize
window2 = [-1] * windowSize
rcv_base = 0
past = 0

command = input("Please enter a command: \n1. LFTP lsend myserver filename\n2. LFTP lget myserver filename\n")

CL = command.split()
filename = CL[3]
if CL[1] == "lsend":
    if not os.path.exists(path+"/"+filename):
        print("file doesn't exists")
        exit(0)

    attr = os.stat(path+"/"+filename)
    packetNum = int(attr.st_size/2048) + 1  # number of packet
    file_handler = open(path+"/"+filename, 'rb')
    message = command + " " + str(packetNum);
    UDPSocket.sendto(message.encode("utf-8"), (serverName, serverPort))

    for i in range(packetNum):
        file_content = file_handler.read(2000)
        UDPSocket.sendto(file_content, (serverName, serverPort))
        """md5_val = hashlib.md5(file_content).hexdigest()
        connectionSocket.send(md5_val.encode("utf-8"))"""
        if i % 100 == 0:
            print("Packet number: " + str(i))

    modifiedMessage, serverAddress = UDPSocket.recvfrom(2048)

    print(modifiedMessage)
    file_handler.close()
    UDPSocket.close()
elif CL[1] == "lget": 
    message = command + " " + str(windowSize)
    rcv_base = 0
    packetNum = -1
    past = -1
    cnt = 0
    filehandler = open(path+"/"+filename, 'wb')
    UDPSocket.sendto(message.encode("utf-8"), (serverName, serverPort))
    while True:
        data, serverAddress = UDPSocket.recvfrom(2048)
        seq = data[0:4]
        seq = unpack('i', seq)[0]
        cnt = max(cnt, seq)

        #print message
        if seq != past + 1:
            print("haha:", past, " ", seq)
        past = seq
        if seq % 100 == 0:
            print(seq)


        #return ack
        head = Header.Header(seq, windowSize - cnt + rcv_base - int(windowSize/5)).getHeader()
        ack = pack('ii', head['seq'], head['rwnd'])
        UDPSocket.sendto(ack, serverAddress)
        if seq == 0:
            packetNum = int(data[8:].decode("utf-8"))
            if packetNum == 0:
                print("file doesn't exists")
                break
            rcv_base += 1
            print(packetNum)
            continue
        if seq >= rcv_base:
            filedata = data[8:]
            window[seq % windowSize] = filedata
            window2[seq % windowSize] = seq

        #check window and read 
        if random.random()<debug:
            while True:
                if window2[rcv_base % windowSize] == rcv_base:
                    filehandler.write(window[rcv_base % windowSize])
                    rcv_base += 1
                else:
                    break

        if rcv_base >= packetNum + 1 and packetNum > 0:
            break


    filehandler.close()

#LFTP lget myserver 2.png
#LFTP lsend myserver img.jpg


