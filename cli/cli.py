import cmd
import json
import socket
from time import sleep
import requests
from threading import Thread
import sys
from lib_sonos.sonos_service import SonosServerService


def normalize_output(command, range, default_value):
    command = "{command} ({range})".format(range=range, command=command).ljust(25)
    default_value = "[{}]".format(default_value).rjust(5)
    return "{command}{default_value}:".format(command=command, default_value=default_value)


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

    def __init__(self, client_hostname="127.0.0.1", client_port=5005, server_hostname="127.0.0.1", server_port=12900):
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

        # subscribe client to Sonos Broker
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
                    raise ("No uid found in sonos udp response!\nResponse: {}")

                speaker = SonosSpeakerCmd(self.commands)
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
        if not speakers:
            print("No speakers found. All speakers offline?")
            return
        for speaker in speakers:
            self.commands.current_state(speaker.uid, 0)

    def help_update(self):
        print("Forces an update of all speakers and their current state. This should be done automatically after any"
              " speaker status change.")

    def help_list(self):
        print('Lists all Sonos speaker in the network')

    def do_list(self, argument):
        self._sonos_speakers.sort(key=lambda x: x.speaker_id, reverse=False)
        print("\nspeaker(s):")
        print("-----------")
        for speaker in self.sonos_speakers:
            print(speaker)
        print("\n")

    def help_speaker(self):
        print("speaker: Lists all available speakers to interact with.")
        print("speaker [num]: Interact with the chosen speaker.")

    def do_speaker(self, speaker_id):
        if not speaker_id:
            self.do_list('')
            return
        try:
            speaker_id = int(speaker_id)
        except ValueError:
            print("Invalid speaker id.")
            return

        speaker = next((x for x in self._sonos_speakers if x.speaker_id == speaker_id), None)

        if not speaker:
            print("No speaker found with id '{id}'.".format(id=speaker_id))
            return

        speaker.cmdloop()

    def do_EOF(self, line):
        """
        Exit from cmd line.
        """
        return True

    def do_exit(self, *args):
        """
        Exit from cmd line.
        """
        return self.stop_listener()

    def postloop(self):
        print


class SonosSpeakerCmd(cmd.Cmd):

    counter = 0

    def __eq__(self, other):
        if isinstance(other, SonosSpeakerCmd):
            return self.uid == other.uid
        if isinstance(other, str):
            return self.uid == other
        raise Exception("Unknown format")

    def __repr__(self):
        return "({session})\t\t{uid}\t[{ip}|{name}|{model}]".format(session=self.speaker_id, uid=self.uid,
                                                                    ip=self.ip, name=self.zone_name,
                                                                    model=self.model)

    @property
    def prompt(self):
        prompt = "unknown"
        if self.uid:
            prompt = self.uid
        return "\n{prompt} =>> ".format(prompt=prompt)

    def __init__(self, commands):
        cmd.Cmd.__init__(self)
        SonosSpeakerCmd.counter += 1
        self.commands = commands
        self.speaker_id = SonosSpeakerCmd.counter
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
        self.is_coordinator = False

    def do_EOF(self, *args):
        """
        Exit from cmd line.
        """
        return True

    def do_exit(self, *args):
        """
        Exit from cmd line.
        """
        return True

    def postloop(self):
        print

    def do_update(self, *args):
        self.commands.current_state(self.uid, False)

    def help_update(self):
        print("Gets the current speaker state. This will update all properties of the speaker.\n")

    def help_volume(self):
        print("volume: Gets the current speaker volume.")
        print("volume [get]: Forces the Broker to retrieve the speakers volume.")
        print("volume [set]: Sets the speakers volume.")

    def do_volume(self, line):
        line = line.lower()
        if not line:
            pass
        elif line == "get":
            self.commands.get_volume(self.uid)
        elif line == "set":
            default_vol = self.volume
            volume = input(normalize_output("Volume", "0-100", default_vol))
            if not volume:
                volume = default_vol
            group_command = input(normalize_output("Group command", "0|1", "0"))
            if not group_command:
                group_command = 0
            self.commands.set_volume(self.uid, volume, group_command)
        else:
            print("unknown argument")
            return
        print("current volume: %s" % self.volume)

    def help_bass(self):
        print("bass: Gets the current speaker bass.")
        print("bass [get]: Forces the Broker to retrieve the speakers bass.")
        print("bass [set]: Sets the speakers bass.")

    def do_bass(self, line):
        line = line.lower()
        if not line:
            pass
        elif line == "get":
            self.commands.get_bass(self.uid)
        elif line == "set":
            default_bass = self.bass
            bass = input(normalize_output("Bass", "-10-10", default_bass))
            if not bass:
                bass = default_bass
            group_command = input(normalize_output("Group command", "0|1", "0"))
            if not group_command:
                group_command = 0
            self.commands.set_bass(self.uid, bass, group_command)
        else:
            print("unknown argument")
            return
        print("current bass: %s" % self.bass)

    def help_treble(self):
        print("treble: Gets the current speaker treble.")
        print("treble [get]: Forces the Broker to retrieve the speakers treble.")
        print("treble [set]: Sets the speakers treble.")

    def do_treble(self, line):
        line = line.lower()
        if not line:
            pass
        elif line == "get":
            self.commands.get_treble(self.uid)
        elif line == "set":
            default_treble = self.treble
            treble = input(normalize_output("Treble", "-10-10", default_treble))
            if not treble:
                treble = default_treble
            group_command = input(normalize_output("Group command", "0|1", "0"))
            if not group_command:
                group_command = 0
            self.commands.set_treble(self.uid, treble, group_command)
        else:
            print("unknown argument")
            return
        print("current treble: %s" % self.treble)

    def help_loudness(self):
        print("loudness: Gets the current speaker loudness value.")
        print("loudness [get]: Forces the Broker to retrieve the speakers loudness value.")
        print("loudness [set]: Sets the speakers loudness value.")

    def do_loudness(self, line):
        line = line.lower()
        if not line:
            pass
        elif line == "get":
            self.commands.get_loudness(self.uid)
        elif line == "set":
            default_loudness = self.loudness
            loudness = input(normalize_output("Loudness", "0|1", default_loudness))
            if not loudness:
                loudness = default_loudness
            group_command = input(normalize_output("Group command", "0|1", "0"))
            if not group_command:
                group_command = 0
            self.commands.set_loudness(self.uid, loudness, group_command)
        else:
            print("unknown argument")
            return
        print("current loudness: %s" % self.loudness)


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
                                                                       port=self.server_port), data=json.dumps(payload),
                                     headers=self.headers)
            if response.status_code != 200:
                html_start = "<html><head><title>Sonos Broker</title></head><body>"
                html_end = "</body></html>"

                raise Exception("Invalid status response '{code}'!\nServer message: {message}"
                                .format(code=response.status_code,
                                        message=response.text.lstrip(html_start).rstrip(html_end)))
        except ConnectionError as err:
            raise Exception("Could not connect to Sonos broker {hostname}:{port}.".format(hostname=self.server_hostname,
                                                                                          port=self.server_port))
        except Exception as err:
            print(err)
            return False

        #we do a 300ms sleep to retrieve the data
        sleep(0.3)
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

    def get_volume(self, uid):
        return self.send(
            {
                'command': 'get_volume',
                'parameter': {
                    'uid': uid.lower()
                }
            }
        )

    def set_volume(self, uid, volume, group_command):
        return self.send(
            {
                'command': 'set_volume',
                'parameter': {
                    'uid': uid,
                    'volume': volume,
                    'group_command': group_command
                }
            }
        )

    def get_bass(self, uid):
        return self.send(
            {
                'command': 'get_bass',
                'parameter': {
                    'uid': uid.lower()
                }
            }
        )

    def set_bass(self, uid, bass, group_command):
        return self.send(
            {
                'command': 'set_bass',
                'parameter': {
                    'uid': uid,
                    'bass': bass,
                    'group_command': group_command
                }
            }
        )

    def get_treble(self, uid):
        return self.send(
            {
                'command': 'get_treble',
                'parameter': {
                    'uid': uid.lower()
                }
            }
        )

    def set_treble(self, uid, treble, group_command):
        return self.send(
            {
                'command': 'set_treble',
                'parameter': {
                    'uid': uid,
                    'treble': treble,
                    'group_command': group_command
                }
            }
        )

    def get_loudness(self, uid):
        return self.send(
            {
                'command': 'get_loudness',
                'parameter': {
                    'uid': uid.lower()
                }
            }
        )

    def set_loudness(self, uid, loudness, group_command):
        return self.send(
            {
                'command': 'set_loudness',
                'parameter': {
                    'uid': uid,
                    'loudness': loudness,
                    'group_command': group_command
                }
            }
        )

if __name__ == '__main__':
    # client_ip = "192.168.178.53"
    #client_port = 5005
    #server_ip = "192.168.178.53"
    #server_port = "12900"
    #cmd = SonosBrokerCmd(client_ip, client_port, server_ip, server_port)
    broker_cmd = SonosBrokerCmd()
    broker_cmd.cmdloop()