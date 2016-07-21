#Created by Pontus 17-07-16

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = '192.168.25.115'
port = 50005
s.bind((host, port))

print('Starting RobotPI server.\nWaiting for clients...')

inp = ""

while inp != 'shutdown':

    #Basically set client to null
    client = None
    inp = ""
    
    s.listen(1)
    while client == None:
        client, addr = s.accept()
        print ('Got connection from', addr)
        client.send('You are connected to RobotPi\n')

    while inp != 'quit':
        inp = client.recv(64)
        print(inp)
        if(inp != 'quit'):
            client.send('Received: ' + inp)

    print('User quit.')
    client.send('You will now disconnect.\nThank you for driving me!')
    client.close()
    