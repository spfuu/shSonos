# -*- coding: utf-8 -*-
__author__ = 'pfischi'

import socket
#from lib_sonos import sonos_speaker
import json

registered_clients = {}

class UdpBroker():

    @staticmethod
    def subscribe_client(ip, port):
        if ip not in registered_clients:
            registered_clients.update({ip: [port]})
        else:
            ports = registered_clients[ip]
            if port not in ports:
                registered_clients[ip].append(port)

    @staticmethod
    def unsubscribe_client(ip, port):
        if ip in registered_clients:
            if port in registered_clients[ip]:
                registered_clients[ip].remove(port)

    @staticmethod
    def udp_send(data):
        try:

            print("sending data to all connected clients: {}".format(data))

            for host, ports in registered_clients.items():
                for port in ports:
                    try:
                        family, type, proto, canonname, sockaddr = socket.getaddrinfo(host, port)[0]
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.sendto(data.encode('utf-8'), (sockaddr[0], sockaddr[1]))
                        sock.close()
                        print("UDP: Sending data to {}:{}: ".format(host, port, data))
                        del sock

                    except Exception as e:
                        raise Exception("UDP: Problem sending data to {}:{}: ".format(host, port, e))
        except Exception as err:
            print(err)
