import socket

__author__ = 'pfischi'

import sys
#sys.path.append('/usr/smarthome/plugins/sonos/server/pycharm-debug-py3k.egg')
#import pydevd

class UdpBroker():

    def __init__(self):
        self.registered_clients = {}

    def subscribe_client(self, ip, port):
        if ip not in self.registered_clients:
            self.registered_clients.update({ip: [port]})
        else:
            ports = self.registered_clients[ip]
            if port not in ports:
                self.registered_clients[ip].append(port)

    def unsubscribe_client(self, ip, port):
        if ip in self.registered_clients:
            if port in self.registered_clients[ip]:
                self.registered_clients[ip].remove(port)

    def udp_send(self, data):
        try:

            print("sending data to all connected clients: {}".format(data))

            for host, ports in self.registered_clients.items():
                for port in ports:
                    try:
                        family, type, proto, canonname, sockaddr = socket.getaddrinfo(host, port)[0]
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.sendto(data.encode('utf-8'), (sockaddr[0], sockaddr[1]))
                        sock.close()
                        print("UDP: Sending data to {}:{}: ".format(host, port, data))
                        del(sock)

                    except Exception as e:
                        raise Exception("UDP: Problem sending data to {}:{}: ".format(host, port, e))
        except Exception as err:
            print(err)
