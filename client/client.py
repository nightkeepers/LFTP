from socket import *
import os
from ClientSend import *
from ClientGet import *
import Header

path = sys.path[0]

#serverName = "2001:250:3002:4251:acb9:7567:3619:ad1b"
serverName = "172.18.33.0"
serverPort = 6666
UDPSocket = socket(AF_INET, SOCK_DGRAM)
#UDPSocket = socket(AF_INET6, SOCK_DGRAM)
UDPSocket.bind(("", 6666))


while True:
    command = input("\nPlease enter a command: \n1. LFTP lsend myserver filename\n2. LFTP lget myserver filename\n3. exit\n")
    CL = command.split()
    if command == "exit":
        break
    if CL[2] != "myserver":
        serverName = CL[2]
    filename = CL[3]
    if CL[1] == "lsend":
        attr = os.stat(path+"/"+filename)
        packetNum = 0
        if not os.path.exists(path+"/"+filename):
            print("file doesn't exists")
        else:
            packetNum = int(attr.st_size/2000) + 1  # number of packet
            file_handler = open(path+"/"+filename, 'rb')
        print("fileSize: ", attr.st_size/1024/1024, " MB")
        message = command + " " + str(packetNum);
        UDPSocket.sendto(message.encode("utf-8"), (serverName, serverPort))
        rwnd, serverAddress = UDPSocket.recvfrom(2048)
        rwnd = rwnd[4:8]
        rwnd = unpack('i', rwnd)[0]
        ClientSend(UDPSocket, serverAddress, packetNum, rwnd).sendFile(filename)

    elif CL[1] == "lget": 
        message = command + " " + str(windowSize)
        UDPSocket.sendto(message.encode("utf-8"), (serverName, serverPort))
        ClientGet(UDPSocket).receive(filename)

    else:
        print("invalid command")


#LFTP lget myserver 2.png
#LFTP lsend myserver img.jpg
#LFTP lsend myserver 超人：钢铁之躯.rmvb


