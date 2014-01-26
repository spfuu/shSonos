import socket
from lib import sonos_speaker

__author__ = 'pfischi'

import sys
#sys.path.append('/usr/smarthome/plugins/sonos/server/pycharm-debug-py3k.egg')
#import pydevd

registered_clients = {}


class UdpResponse():
    @staticmethod
    def get_speaker(uid):
        if uid in sonos_speaker.sonos_speakers:
            return sonos_speaker.sonos_speakers[uid]
        return None

    @staticmethod
    def mute(uid):
        speaker = UdpResponse.get_speaker(uid)
        if speaker:
            return "speaker/{}/mute/{}".format(uid, speaker.mute)

    @staticmethod
    def led(uid):
        speaker = UdpResponse.get_speaker(uid)
        if speaker:
            return "speaker/{}/led/{}".format(uid, speaker.led)

    @staticmethod
    def volume(uid):
        speaker = UdpResponse.get_speaker(uid)
        if speaker:
            return "speaker/{}/volume/{}".format(uid, speaker.volume)

    @staticmethod
    def streamtype(uid):
        speaker = UdpResponse.get_speaker(uid)
        if speaker:
            return "speaker/{}/streamtype/{}".format(uid, speaker.streamtype)

    @staticmethod
    def stop(uid):
        speaker = UdpResponse.get_speaker(uid)
        if speaker:
            return "speaker/{}/stop/{}".format(uid, speaker.stop)

    @staticmethod
    def play(uid):
        speaker = UdpResponse.get_speaker(uid)
        if speaker:
            return "speaker/{}/play/{}".format(uid, speaker.play)

    @staticmethod
    def pause(uid):
        speaker = UdpResponse.get_speaker(uid)
        if speaker:
            return "speaker/{}/pause/{}".format(uid, speaker.pause)

    @staticmethod
    def track(uid):
        speaker = UdpResponse.get_speaker(uid)
        if speaker:
            return "speaker/{}/track/{}".format(uid, speaker.track)

    @staticmethod
    def artist(uid):
        speaker = UdpResponse.get_speaker(uid)
        if speaker:
            return "speaker/{}/artist/{}".format(uid, speaker.artist)


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
                        del (sock)

                    except Exception as e:
                        raise Exception("UDP: Problem sending data to {}:{}: ".format(host, port, e))
        except Exception as err:
            print(err)
