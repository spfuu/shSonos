import cmd
import json
import operator
import socket
import requests
from threading import Thread
import sys
from lib_sonos.sonos_service import SonosServerService


class SonosSpeakerCmd(cmd.Cmd):

    counter = 0

    def __eq__(self, other):
        if isinstance(other, SonosSpeakerCmd):
            return self.uid == other.uid
        if isinstance(other, str):
            return self.uid == other
        raise Exception("Unknown format")

    def __repr__(self):
        return "({session})\t\t{uid}\t[{ip}|{name}|{model}]".format(session=self.session_id, uid=self.uid,
                                                                      ip=self.ip, name=self.zone_name,
                                                                      model=self.model)

    def __init__(self):
        SonosSpeakerCmd.counter += 1
        self.session_id = SonosSpeakerCmd.counter
        self.uid = None
        self.ip = None
        self.model = None
        self.zone_name = None
        self.zone_icon = None
        self.serial_number = None
        self.software_version = None
        self.hardware_version = None
        self.mac_address = None
        self.playlist_position = None
        self.volume = None
        self.mute = None
        self.led = False
        self.streamtype = None
        self.stop = None
        self.play = None
        self.pause = None
        self.track_title = None
        self.track_artist = None
        self.track_duration = None
        self.track_position = None
        self.track_album_art = None
        self.track_uri = None
        self.radio_station = None
        self.radio_show = None
        self.status = False
        self.max_volume = None
        self.additional_zone_members = None
        self.bass = None
        self.treble = None
        self.loudness = None
        self.playmode = None
        self.alarms = None


class Commands():
    @property
    def headers(self):
        return {'Content-type': 'application/json', 'Accept': 'text/plain'}

    @property
    def client_hostname(self):
        return self.client_hostname()

    @property
    def client_port(self):
        return self.client_port

    @property
    def server_hostname(self):
        return self._server_hostname

    @property
    def server_port(self):
        return self._server_port

    def __init__(self, server_hostname, server_port):
        self._server_hostname = server_hostname
        self._server_port = server_port

    def send(self, payload):
        try:
            response = requests.post("http://{hostname}:{port}".format(hostname=self.server_hostname,
                                    port=self.server_port), data=json.dumps(payload), headers=self.headers)
            if response.status_code != 200:
                raise Exception("Invalid status response '{code}'!\nServer message: {message}"
                                .format(code=response.status_code, message=response.text))
        except ConnectionError as err:
            raise Exception("Could not connect to Sonos broker {hostname}:{port}.".format(hostname=self.server_hostname,
                                                                                port=self.server_port))
        except Exception as err:
            sys.stdout.write(" failed!\n")
            print(err)
            return False

        return True


    def subscribe(self, hostname, port):
        """
        Connects the client to the Sonos broker
        :param hostname: server host
        :param port: server port
        :return: True / False
        """
        return self.send(
            {
                'command': 'client_subscribe',
                'parameter': {
                    'ip': hostname,
                    'port': port,
                }
            }
        )


    def current_state(self, uid, group_command):
        return self.send(
            {
                'command': 'current_state',
                'parameter': {
                    'uid': uid.lower(),
                    'group_command': group_command
                }
            }
        )


class SonosBrokerCmd(cmd.Cmd):

    @property
    def commands(self):
        return self._commands

    @property
    def sonos_speakers(self):
        return self._sonos_speakers

    @property
    def udp_socket(self):
        return self._udp_socket

    @property
    def client_hostname(self):
        return self._client_hostname

    @property
    def client_port(self):
        return self._client_port

    @property
    def server_hostname(self):
        return self._server_hostname

    @property
    def server_port(self):
        return self._server_port

    def __init__(self, client_hostname, client_port, server_hostname, server_port):
        cmd.Cmd.__init__(self)
        self._sonos_speakers = []
        self._commands = Commands(server_hostname, server_port)
        self._client_hostname = client_hostname
        self._client_port = client_port
        self._server_hostname = server_hostname
        self._server_port = server_port
        self._connected = True
        self._udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._udp_listener_thread = Thread(target=self.start_listener)
        self._udp_listener_thread.daemon = True
        self._udp_listener_thread.start()

        sys.stdout.write("Connecting to Sonos broker ...")
        sys.stdout.flush()

        #subscribe client to Sonos Broker
        if not self.commands.subscribe(self.client_hostname, self.client_port):
            exit()
        else:
            sys.stdout.write(" done!\n\n")
            sys.stdout.flush()
            self.prompt = "=>> "
            self.intro = "Welcome to Sonos Broker console!"


    def start_listener(self):
        """
        Starts a udp listener to retrieve Sonos Broker events
        """
        self._udp_socket.bind((self.client_hostname, self.client_port))

        while self._connected:

            try:
                data, address = self.udp_socket.recvfrom(10000)
                address = "{}:{}".format(address[0], address[1])
                print("{}: incoming connection from {}".format('sonos', address))
            except Exception as err:
                print("{}".format(err))
                continue

            try:
                sonos = json.loads(data.decode('utf-8').strip())
                uid = sonos['uid']

                if not uid:
                    raise("No uid found in sonos udp response!\nResponse: {}")

                speaker = SonosSpeakerCmd()
                if not uid in self._sonos_speakers:
                    self._sonos_speakers.append(speaker)
                else:
                    speaker = next((x for x in self._sonos_speakers if x.uid == uid), None)

                for item, value in sonos.items():
                    if item.lower() == "status":
                        if not value:
                            self.sonos_speakers.remove(speaker)
                            print("Speaker with uid {uid} now offline.".format(uid=speaker.uid))

                    setattr(speaker, item, value)

            except Exception as err:
                print(err)
                continue


    def stop_listener(self):
        """
        Stops the udp listener and closes the socket.
        :return:
        """
        sys.stdout.write("Stopping udp listener ...")
        self._connected = False
        if self.udp_socket:
             self.udp_socket.close()
        self._udp_listener_thread.join(1)
        sys.stdout.write(" done!")
        sys.stdout.flush()
        return True

    def do_update(self, argument):
        speakers = SonosServerService._discover()
        for speaker in speakers:
            self.commands.current_state(speaker.uid, 0)

    def help_update(self):
        print("Forces an update of all speakers and their current state. This should be done automatically after any"
              " speaker status change.")

    def help_list(self):
        print('Lists all Sonos speaker in the network')

    def do_list(self, argument):
        self._sonos_speakers.sort(key=lambda x: x.session_id, reverse=False)
        print("\nsession(s):")
        print("-----------")
        for speaker in self.sonos_speakers:
            print(speaker)

    def do_EOF(self, line):
        """
        Exit from cmd line.
        :param line:
        :return:
        """
        return True

    def do_exit(self, *args):
        """
        Exit from cmd line.
        :param args:
        :return:
        """
        return self.stop_listener()

    def postloop(self):
        print

if __name__ == '__main__':

    client_ip = "192.168.178.53"
    client_port = 5005
    server_ip = "192.168.178.53"
    server_port = "12900"

    cmd = SonosBrokerCmd(client_ip, client_port, server_ip, server_port)
    cmd.cmdloop()