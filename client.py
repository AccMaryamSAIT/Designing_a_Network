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


def splitFile(fileName):
    # Split filename for relevant information
    fileType, fileDate, fileEnd = fileName.split("_")
    year, month, day = fileDate.split("-")
    fileTime, fileType = fileEnd.split(".")
    hour, minutes = fileTime.split("-")
    dateTime = []
    dateTime.append(year)
    dateTime.append(month)
    dateTime.append(day)
    dateTime.append(hour)
    dateTime.append(minutes)
    return dateTime


def chooseNewestFile(folder):
    # Get list of filenames using os.listdir()
    fileList = os.listdir(folder)

    ### Find the latest file
    # Assign the first file as the newest
    newestFile = fileList[0]
    newestFileDateTime = splitFile(newestFile)

    # Loop through fileList
    for fileName in fileList:
        fileDateTime = splitFile(fileName)
        # Compare current file to newest file
        for i in range(len(fileDateTime)):
            # As you're comparing sections of date/time, if value is greater, then file is newer
            if fileDateTime[i] > newestFileDateTime[i]:
                newestFile = fileName
                break

    return newestFile


logsFolder = "/tmp/SysCheckLogs/"
newestFile = chooseNewestFile(logsFolder)

filename = logsFolder + newestFile
filesize = os.stat(filename)
filesize = filesize.st_size

try:
    with open(filename, 'rb') as f:
        hash = hashlib.md5(f.read()).hexdigest()
        print(f'File hash is: {hash}')
except:
    print(f"Error: {filename} file cannot be opened!")
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
else:
    print('Handshake process failed.')

print('File sent successfully. Awaiting confirmation.')

reply = client_socket.recv(buffer_size).decode()
if reply == 'SUCCESS':
    print('Transfer complete.')
elif reply == 'ERROR_CHECKSUM':
    print('Checksum error. File corrupted during transfer.')
else:
    print(f'Unkown message recieved: {reply}')

client_socket.close()
