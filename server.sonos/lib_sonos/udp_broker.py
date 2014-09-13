# -*- coding: utf-8 -*-
import logging
import errno
import socket

logger = logging.getLogger('')
registered_clients = {}


class UdpBroker():
    @staticmethod
    def subscribe_client(ip, port):
        logger.info('register client for udp messages: {host}:{port}'.format(host=ip, port=port))
        if ip not in registered_clients:
            registered_clients.update({ip: [port]})
        else:
            ports = registered_clients[ip]
            if port not in ports:
                registered_clients[ip].append(port)

        logger.info("registered clients: {clients}".format(clients=", ".join(['{ip}:{port}'.format(ip=key, port=value)
                                                                              for (key, value) in
                                                                              registered_clients.items()])))

    @staticmethod
    def unsubscribe_client(ip, port):
        logger.info('un-register client for udp messages: {host}:{port}'.format(host=ip, port=port))
        if ip in registered_clients:
            if port in registered_clients[ip]:
                registered_clients[ip].remove(port)

            if len(registered_clients[ip]) == 0:
                registered_clients.pop(ip)

        logger.info("registered clients: {clients}".format(
            clients=", ".join(['{ip}:{port}'.format(ip=key, port=value) for (key, value)
                               in registered_clients.items()])))

    @staticmethod
    def udp_send(data):
        logger.info("registered clients: {clients}".format(
            clients=", ".join(['{ip}:{port}'.format(ip=key, port=value) for (key, value)
                               in registered_clients.items()])))
        logger.info("sending sonos speaker data: {}".format(data))
        for host, ports in registered_clients.items():
            for port in ports:
                try:
                    family, type, proto, canonname, sockaddr = socket.getaddrinfo(host, port)[0]
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    try:
                        sock.sendto(data.encode('utf-8'), (sockaddr[0], sockaddr[1]))
                    except socket.error as e:
                        if isinstance(e.args, tuple):
                            if e[0] == errno.EPIPE:
                                # remote peer disconnected
                                logger.warning("Detected remote disconnect")
                            else:
                                logger.warning(e)
                                pass
                        else:
                            logger.error("socket error {}".format(e))

                        sock.close()

                    except IOError as e:
                        logger.error("Got IO error: {}".format(e))
                except Exception as err:
                    logger.error(err)
                    # remove client from the list
                    UdpBroker.unsubscribe_client(host, port)
                    pass