#!/usr/bin/env python3

import socket
import sys

HOST, PORT = "localhost", 9999
data = " ".join(sys.argv[1:])

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    sock.sendall('{}\n'.format(data).encode('UTF-8'))

    # Receive data from the server and shut down
    received = sock.recv(4096)
finally:
    sock.close()

print(received.decode('UTF-8'))