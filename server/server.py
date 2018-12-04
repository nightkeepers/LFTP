from socket import *
from ServerSend import *
from ServerGet import *

IP_PORT = ('', 6666)
commandServerSocket = socket(AF_INET, SOCK_DGRAM)
commandServerSocket.bind(IP_PORT)
port = [i for i in range(6667,6677)]
print('server is listening on port 6666')

while True:
    command, clientAddress = commandServerSocket.recvfrom(2048)
    #print(command.decode('utf-8'))
    command = command.decode('utf8').split()
    if len(port) > 0:
        serverSocket = socket(AF_INET, SOCK_DGRAM)
        p = port.pop(0)
        serverSocket.bind(('', p))
        if command[1] == 'lsend':
            print(str(clientAddress) + ' is uploading on port ' + str(p))
            threading.Thread(target=ServerGet(serverSocket, clientAddress, int(command[4])).getFile, args=(command[3], port, p)).start()
        
        elif command[1] == 'lget':
            print(str(clientAddress) + ' is downloading on port ' + str(p))
            threading.Thread(target=ServerSend(serverSocket, clientAddress, int(command[4])).sendFile, args=(command[3], port, p)).start()

        else:
            string = 'Error Input!'
            commandServerSocket.sendto(string.encode('utf-8'), clientAddress)
    else:
        string = 'The maximum number of clients has been reached!'
        commandServerSocket.sendto(string.encode('utf-8'), clientAddress)
    
