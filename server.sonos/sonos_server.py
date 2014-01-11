#!/usr/bin/env python3

import socketserver
import argparse
from sonos_commands import Command
from sonos_database import SonosDatabase
from utils import really_unicode


class SonosTCPHandler(socketserver.StreamRequestHandler):

    def handle(self):

        # self.request is the TCP socket connected to the client
        """
        The RequestHandler class for our server.

        It is instantiated once per connection to the server, and must
        override the handle() method to implement communication to the
        client.
        """

        self.database = SonosDatabase(database)

        while True:
		
            self.data = self.rfile.readline().strip().lower()
            #self.data = self.request.recv(1024).strip().lower()

            if not self.data:
                break

            print(self.data)

            command = really_unicode(self.data)
            s_command = Command(command, self.database)
            self.request.sendall(s_command.do_work())


parser = argparse.ArgumentParser()
parser.add_argument('-d', help='Path to sqlite database', required='True', dest='database')

args = parser.parse_args()
database = args.database


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), SonosTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

