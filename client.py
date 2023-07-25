"""
Name: Server.py
Authors: Roman Kapitoulski, Eric Russon, Maryam Bunama
Version: 1.0
Date: July 25, 2023
Description: This script takes the JSON file generated by SysAdminTask.py and sends it to the Server.py software on 
the server machine. It performs acknowledgments and error-checking throughout the process.
"""

import socket, hashlib, time, tqdm, os

server_ip = '127.0.0.1'
server_port = 5000
buffer_size = 1024
EOF = ':EOF:'
sep = '}}'

def chooseNewestFile():
    date = 1
    return date

date = chooseNewestFile()

filename = f'SystemResults_{date}.json'
filesize = os.stat(filename)
filesize = filesize.st_size

try:
    with open(filename, 'rb') as f:
        hash = hashlib.md5(f.read()).hexdigest()
        print(f'File hash is: {hash}')
except:
    print("Error: " + filename + " file cannot be opened!")
    print("Quitting code...")
    exit(0)

client_socket = socket.socket()
client_socket.connect((server_ip, server_port))
print('Connected to server.') 

msg = filename+sep+EOF+sep+hash+sep+str(filesize)
progress = tqdm.tqdm(range(filesize), f'Sending file {filename}', unit='B', unit_scale=True, unit_divisor=1024)

client_socket.sendall(msg.encode())
reply = client_socket.recv(buffer_size).decode() 

if reply == 'OK':
    with open(filename, 'rb') as f:
        while True:
            data = f.read(buffer_size)
            if not data:
                progress.close()
                time.sleep(1)
                client_socket.sendall(EOF.encode())
                break
            else:
                client_socket.sendall(data)
                progress.update(len(data))

print('File sent successfully. Awaiting confirmation.')

reply = client_socket.recv(buffer_size).decode()
if reply == 'SUCCESS':
    print('Transfer complete.')
elif reply == 'ERROR_CHECKSUM':
    print('Checksum error. File corrupted during transfer.')
else:
    print(f'Unkown message recieved: {reply}')

client_socket.close()

