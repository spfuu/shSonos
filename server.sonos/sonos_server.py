#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer


import sys
import socketserver
import argparse
import xml
from xml.dom import minidom
from sonos_commands import Command
from sonos_service import SonosService

#sys.path.append('/usr/smarthome/plugins/sonos/server/pycharm-debug-py3k.egg')
#import pydevd

class SonosHttpHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        result, response = command.do_work(self.client_address[0], self.path)

        status = 'Error'
        if result:
            self.send_response(200, 'OK')
            status = 'Success'
        else:
            self.send_response(400, 'Bad request')

        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("<html><head><title>{}</title></head>".format(status).encode('utf-8'))
        self.wfile.write("<body><p>{}</p></body>".format(response).encode('utf-8'))


    def do_NOTIFY(self):
        self.send_response(200, "OK")
        content_len = int(self.headers['content-length'])
        post_body = self.rfile.read(content_len).decode('utf-8')
        print(post_body)


class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

parser = argparse.ArgumentParser()
parser.add_argument('--port', help='Http server port', type=int, dest='port', default=12900)
parser.add_argument('--host', help='Http server host', dest='host', default='0.0.0.0')
parser.add_argument('--localip', help='IP of this server in the local network', dest='localip', required=True)

args = parser.parse_args()
port = args.port
host = args.host
localip = args.localip
sonos_service = SonosService(localip, port)
command = Command(sonos_service)


if __name__ == "__main__":
    http_server = ThreadedHTTPServer((host, port), SonosHttpHandler)
    print('Starting http server, use <Ctrl-C> to stop')
    http_server.serve_forever()
