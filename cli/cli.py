#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cmd
import json
import os
import socket
from time import sleep
import requests
from threading import Thread
import sys


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
                #print("{}: incoming connection from {}".format('sonos', address))
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
        status, data = self.commands.client_list()
        if not status:
            return
        speakers = data.split('\n')
        speakers = filter(None, speakers)
        if not speakers:
            print("No speakers found. All speakers offline?")
            return
        for speaker in speakers:
            self.commands.current_state(speaker, 0)

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
        self.tts_local_mode = False
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
        print("volume: Gets the current volume level.")
        print("volume [get]: Forces the Broker to retrieve the speakers volume level.")
        print("volume [set]: Sets the volume.")

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
        print("volume: {}".format(self.volume))

    def help_bass(self):
        print("bass: Gets the current bass level.")
        print("bass [get]: Forces the Broker to retrieve the speakers bass level.")
        print("bass [set]: Sets the bass.")

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
        print("bass: {}".format(self.bass))

    def help_treble(self):
        print("treble: Gets the current 'treble' value.")
        print("treble [get]: Forces the Broker to retrieve the speakers 'treble' value.")
        print("treble [set]: Sets the 'treble' value.")

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
        print("treble: {}".format(self.treble))

    def help_loudness(self):
        print("loudness: Gets the current loudness value.")
        print("loudness [get]: Forces the Broker to retrieve the speakers loudness value.")
        print("loudness [set]: Turns loudness on or off.")

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
        print("loudness: {}".format(self.loudness))

    def help_play(self):
        print("play: Gets the current 'Play' status.")
        print("play [get]: Forces the Broker to retrieve the speakers 'Play' status.")
        print("play [set]: Starts or stops the playback.")

    def do_play(self, line):
        line = line.lower()
        if not line:
            pass
        elif line == "get":
            self.commands.get_play(self.uid)
        elif line == "set":
            default_play = self.play
            play = input(normalize_output("Play", "0|1", default_play))
            if not play:
                play = default_play
            self.commands.set_play(self.uid, play)
        else:
            print("unknown argument")
            return
        print("play: {}".format(self.play))

    def help_pause(self):
        print("pause: Gets the current 'Pause' status.")
        print("pause [get]: Forces the Broker to retrieve the speakers 'Pause' status.")
        print("pause [set]: Pauses or resumes the playback.")

    def do_pause(self, line):
        line = line.lower()
        if not line:
            pass
        elif line == "get":
            self.commands.get_pause(self.uid)
        elif line == "set":
            default_pause = self.pause
            pause = input(normalize_output("Pause", "0|1", default_pause))
            if not pause:
                pause = default_pause
            self.commands.set_pause(self.uid, pause)
        else:
            print("unknown argument")
            return
        print("pause: {}".format(self.pause))

    def help_stop(self):
        print("stop: Gets the current 'Stop' status.")
        print("stop [get]: Forces the Broker to retrieve the speakers 'Stop' status.")
        print("stop [set]: Stops or starts the playback.")

    def do_stop(self, line):
        line = line.lower()
        if not line:
            pass
        elif line == "get":
            self.commands.get_stop(self.uid)
        elif line == "set":
            default_stop = self.stop
            stop = input(normalize_output("Stop", "0|1", default_stop))
            if not stop:
                stop = default_stop
            self.commands.set_stop(self.uid, stop)
        else:
            print("unknown argument")
            return
        print("stop: {}".format(self.stop))

    def help_mute(self):
        print("stop: Gets the current 'Mute' status.")
        print("stop [get]: Forces the Broker to retrieve the speakers 'Mute' status.")
        print("stop [set]: 'Mutes or unmutes the speaker.")

    def do_mute(self, line):
        line = line.lower()
        if not line:
            pass
        elif line == "get":
            self.commands.get_mute(self.uid)
        elif line == "set":
            default_mute = self.mute
            mute = input(normalize_output("Mute", "0|1", default_mute))
            if not mute:
                mute = default_mute
            group_command = input(normalize_output("Group command", "0|1", "0"))
            if not group_command:
                group_command = 0
            self.commands.set_mute(self.uid, mute, group_command)
        else:
            print("unknown argument")
            return
        print("mute: {}".format(self.mute))

    def help_led(self):
        print("led: Gets the current 'led' status.")
        print("led [get]: Forces the Broker to retrieve the speakers 'led' status.")
        print("led [set]: Turns the speakers led on or off.")

    def do_led(self, line):
        line = line.lower()
        if not line:
            pass
        elif line == "get":
            self.commands.get_led(self.uid)
        elif line == "set":
            default_led = self.led
            led = input(normalize_output("Led", "0|1", default_led))
            if not led:
                led = default_led
            group_command = input(normalize_output("Group command", "0|1", "0"))
            if not group_command:
                group_command = 0
            self.commands.set_led(self.uid, led, group_command)
        else:
            print("unknown argument")
            return
        print("led: {}".format(self.led))

    def help_playmode(self):
        print("playmode: Gets the current playmode.")
        print("playmode [get]: Forces the Broker to retrieve the speakers playmode.")
        print("playmode [set]: Sets the playmode.")

    def do_playmode(self, line):
        line = line.lower()
        if not line:
            pass
        elif line == "get":
            self.commands.get_playmode(self.uid)
        elif line == "set":
            default_playmode = self.playmode
            playmode = input(normalize_output("Playmode", "normal|shuffle_norepeat|shuffle|repeat_all", default_playmode))
            if not playmode:
                playmode = default_playmode
            self.commands.set_playmode(self.uid, playmode)
        else:
            print("unknown argument")
            return
        print("playmode: {}".format(self.playmode))

    def help_track_position(self):
        print("track_position: Gets the current track position.")
        print("track_position [get]: Forces the Broker to retrieve the current track position.")
        print("track_position [set]: Sets the track position.")

    def do_track_position(self, line):
        line = line.lower()
        if not line:
            pass
        elif line == "get":
            self.commands.get_trackposition(self.uid, force_refresh=1)
        elif line == "set":
            default_position = "00:00:00"
            position = input(normalize_output("Track position", "HH:MM:ss", default_position))
            if not position:
                position = default_position
            self.commands.set_trackposition(self.uid, position)
        else:
            print("unknown argument")
            return
        print("track_position: {}".format(self.track_position))

    def help_volume_up(self):
        print("volume_up: Increases the current volume by 2")

    def do_volume_up(self, line):
        group_command = input(normalize_output("Group command", "0|1", "0"))
        if not group_command:
            group_command = 0
        self.commands.volumeup(self.uid, group_command)
        print("volume: {}".format(self.volume))

    def help_volume_down(self):
        print("volume_down: Decreases the current volume by 2")

    def do_volume_down(self, line):
        group_command = input(normalize_output("Group command", "0|1", "0"))
        if not group_command:
            group_command = 0
        self.commands.volumedown(self.uid, group_command)
        print("volume: {}".format(self.volume))

    def help_next(self):
        print("next: Plays the next music track in the queue.")

    def do_next(self, line):
        self.commands.next(self.uid)
        if self.track_artist and self.track_title:
            print("track: {} - {}".format(self.track_artist, self.track_title))

    def help_previous(self):
        print("previous: Plays the previous music track in the queue.")

    def do_previous(self, line):
        self.commands.previous(self.uid)
        if self.track_artist and self.track_title:
            print("track: {} - {}".format(self.track_artist, self.track_title))

    def help_max_volume(self):
        print("max_volume: Gets the current maximum volume.")
        print("max_volume [get]: Forces the Broker to retrieve the speakers maximum volume.")
        print("max_volume [set]: Sets the maximum volume for the speaker.")

    def do_max_volume(self, line):
        line = line.lower()
        if not line:
            pass
        elif line == "get":
            self.commands.get_maxvolume(self.uid)
        elif line == "set":
            default_max_volume = self.max_volume
            max_volume = input(normalize_output("Maximum volume", "0-100", default_max_volume))
            if not max_volume:
                max_volume = default_max_volume
            group_command = input(normalize_output("Group command", "0|1", "0"))
            if not group_command:
                group_command = 0
            self.commands.set_maxvolume(self.uid, max_volume, group_command)
        else:
            print("unknown argument")
            return
        print("volume: {}".format(self.volume))
        print("max_volume: {}".format(self.max_volume))

    def help_track_url(self):
        print("track_url: Gets the current track url.")
        print("track_url [get]: Forces the Broker to retrieve the current track url.")

    def do_track_url(self, line):
        line = line.lower()
        if not line:
            pass
        elif line == "get":
            self.commands.get_track_uri(self.uid)
        else:
            print("unknown argument")
            return
        print("track_url: {}".format(self.track_uri))

    def help_track_title(self):
        print("track_title: Gets the current track title.")
        print("track_title [get]: Forces the Broker to retrieve the current track title.")

    def do_track_title(self, line):
        line = line.lower()
        if not line:
            pass
        elif line == "get":
            self.commands.get_track_title(self.uid)
        else:
            print("unknown argument")
            return
        print("track_title: {}".format(self.track_title))

    def help_track_artist(self):
        print("track_artist: Gets the current track artist.")
        print("track_artist [get]: Forces the Broker to retrieve the current track artist.")

    def do_track_artist(self, line):
        line = line.lower()
        if not line:
            pass
        elif line == "get":
            self.commands.get_track_artist(self.uid)
        else:
            print("unknown argument")
            return
        print("track_artist: {}".format(self.track_artist))

    def help_radio_station(self):
        print("radio_station: Gets the current radio station.")
        print("radio_station [get]: Forces the Broker to retrieve the current radio station.")

    def do_radio_station(self, line):
        line = line.lower()
        if not line:
            pass
        elif line == "get":
            self.commands.get_radio_station(self.uid)
        else:
            print("unknown argument")
            return
        print("radio_station: {}".format(self.radio_station))

    def help_radio_show(self):
        print("radio_show: Gets the current radio show.")
        print("radio_show [get]: Forces the Broker to retrieve the current radio show.")

    def do_radio_show(self, line):
        line = line.lower()
        if not line:
            pass
        elif line == "get":
            self.commands.get_radio_show(self.uid)
        else:
            print("unknown argument")
            return
        print("radio_show: {}".format(self.do_radio_show()))

    def help_play_url(self):
        print("play_url: Plays the given url.")

    def do_play_url(self, line):
        line = line.lower()
        if not line:
            pass
        url = input(normalize_output("Url", "http://.. or Sonos url", ""))
        if not url:
            return
        self.commands.play_url(self.uid, url)

    def help_play_snippet(self):
        print("play_snippet: Plays a audio snippet. After the snippet was played (maximum 60 seconds, longer snippets "
              "will be truncated) the previous played song will be resumed. You can queue up to 10 snippets. They're "
              "played in the order they are called.")

    def do_play_snippet(self, line):
        line = line.lower()
        if not line:
            pass
        url = input(normalize_output("Url", "http://.. or Sonos url", ""))
        if not url:
            return
        volume = input(normalize_output("snippet volume", "-1-100", "-1"))
        if not volume:
            volume = -1
        fade_in = input(normalize_output("fade in", "0|1", "0"))
        if not fade_in:
            fade_in = 0
        group_command = input(normalize_output("group command", "0|1", "0"))
        if not group_command:
            group_command = 0

        self.commands.play_snippet(self.uid, url, volume, fade_in, group_command)

    def help_play_tts(self):
        print("play_tts: Plays a text-to-speech snippet using the Google TTS API. The previous played song will be "
              "resumed. If you're using the streaming mode, the snippet will be truncated after 10 seconds. You "
              "can queue up to 10 snippets. They're played in the order they are called. To setup the Broker for TTS "
              "support, please take a deeper look at the Sonos Broker documentation.")

    def do_play_tts(self, line):

        if not self.tts_local_mode:
            print("Warning! Google TTS 'local mode' disbaled. Only the 'streaming mode' is available.")
            print("Please read the Sonos Broker documentation to setup Google TTS.")

        tts = input(normalize_output("tts", "max 100 chars", ""))
        if not tts:
            return
        volume = input(normalize_output("snippet volume", "-1-100", "-1"))
        if not volume:
            volume = -1
        fade_in = input(normalize_output("fade in", "0|1", "0"))
        if not fade_in:
            fade_in = 0

        default_language = 'de'
        language = input(normalize_output("language", "en|de|es|fr|it", default_language))
        if not language:
            language = default_language

        stream_mode = 1
        if self.tts_local_mode:
            stream_mode = input(normalize_output("force stream mode", "0|1", "0"))
            if not stream_mode:
                stream_mode = 0

        group_command = input(normalize_output("group command", "0|1", "0"))
        if not group_command:
            group_command = 0

        self.commands.play_tts(self.uid, tts, volume, language, fade_in, stream_mode, group_command)

    def help_is_coordinator(self):
        print("is_coordinator: Returns the status whether the speaker is a group coordinator or not.")
        print("is_coordinator [get]: Forces the Broker to retrieve the coordinator status.")

    def do_is_coordinator(self, line):
        line = line.lower()
        if not line:
            pass
        elif line == "get":
            self.commands.is_coordinator(self.uid)
        else:
            print("unknown argument")
            return
        print("is_coordinator: {}".format(self.is_coordinator))

    def help_tts_local_mode(self):
        print("tts_local_mode: Returns the status whether the Google TTS 'local mode' is enabled or not.")
        print("tts_local_mode [get]: Forces the Broker to retrieve the GoogleTTS 'local mode' status.")

    def do_tts_local_mode(self, line):
        line = line.lower()
        if not line:
            pass
        elif line == "get":
            self.commands.tts_local_mode(self.uid)
        else:
            print("unknown argument")
            return
        print("tts_local_mode: {}".format(self.tts_local_mode))

    def help_playlist(self):
        print("playlist: Gets the current playlist.")
        print("playlist [get]: Gets the current playlist.")
        print("playlist [set]: Sets the current playlist.")

    def do_playlist(self, line):
        line = line.lower()
        if not line or line == "get":
            default_path = ""
            path = input(normalize_output("Playlist", "save path", default_path))

            try:
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
            except Exception:
                print("Couldn't create '{path}'.'!".format(path=os.path.dirname(path)))
                return

            status, response = self.commands.get_playlist(self.uid)

            if not status:
                print("Couldn't get playlist from speaker. Error: {response}".format(response=response))
                return

            with open(path, 'w') as f:
                f.write(response)
                print("Playlist saved to '{path}'.".format(path=path))

        elif line == "set":
            default_path = ""
            path = input(normalize_output("Playlist", "path to file", default_path))

            if not os.path.isfile(path):
                return

            with open(path, 'r') as f:
                playlist = f.read()
                status, response = self.commands.set_playlist(self.uid, playlist)

                if not status:
                    print(response)
        else:
            print("unknown argument")
            return


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
            html_start = "<html><head><title>Sonos Broker</title></head><body>"
            html_end = "</body></html>"

            response_text = response.text.replace(html_start,"",1).replace(html_end,"",1)

            if response.status_code != 200:
                raise Exception("Invalid status response '{code}'!\nServer message: {message}"
                                .format(code=response.status_code, message=response_text))
        except ConnectionError:
            raise Exception("Could not connect to Sonos broker {hostname}:{port}.".format(hostname=self.server_hostname,
                                                                                          port=self.server_port))
        except Exception as err:
            print(err)
            return False, err

        sleep(0.5)
        return True, response_text


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
                    'uid': uid.lower(),
                    'volume': volume,
                    'group_command': group_command
                }
            }
        )

    def get_mute(self, uid):
        return self.send(
            {
                'command': 'get_mute',
                'parameter': {
                    'uid': uid.lower()
                }
            }
        )

    def set_mute(self, uid, mute, group_command):
        return self.send(
            {
                'command': 'set_mute',
                'parameter': {
                    'uid': uid.lower(),
                    'mute': mute,
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
                    'uid': uid.lower(),
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
                    'uid': uid.lower(),
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
                    'uid': uid.lower(),
                    'loudness': loudness,
                    'group_command': group_command
                }
            }
        )

    def get_play(self, uid):
        return self.send(
            {
                'command': 'get_play',
                'parameter': {
                    'uid': uid.lower()
                }
            }
        )

    def set_play(self, uid, play):
        return self.send(
            {
                'command': 'set_play',
                'parameter': {
                    'uid': uid.lower(),
                    'play': play,
                }
            }
        )

    def get_pause(self, uid):
        return self.send(
            {
                'command': 'get_pause',
                'parameter': {
                    'uid': uid.lower()
                }
            }
        )

    def set_pause(self, uid, pause):
        return self.send(
            {
                'command': 'set_pause',
                'parameter': {
                    'uid': uid.lower(),
                    'pause': pause,
                }
            }
        )

    def get_stop(self, uid):
        return self.send(
            {
                'command': 'get_stop',
                'parameter': {
                    'uid': uid.lower()
                }
            }
        )

    def set_stop(self, uid, stop):
        return self.send(
            {
                'command': 'set_stop',
                'parameter': {
                    'uid': uid.lower(),
                    'stop': stop,
                }
            }
        )

    def get_led(self, uid):
        return self.send(
            {
                'command': 'get_led',
                'parameter': {
                    'uid': uid.lower()
                }
            }
        )

    def set_led(self, uid, led, group_command):
        return self.send(
            {
                'command': 'set_led',
                'parameter': {
                    'uid': uid.lower(),
                    'led': led,
                    'group_command': group_command
                }
            }
        )

    def get_playmode(self, uid):
        return self.send(
            {
                'command': 'get_playmode',
                'parameter': {
                    'uid': uid.lower()
                }
            }
        )

    def set_playmode(self, uid, playmode):
        return self.send(
            {
                'command': 'set_playmode',
                'parameter': {
                    'uid': uid.lower(),
                    'playmode': playmode,
                }
            }
        )

    def volumeup(self, uid, group_command):
        return self.send(
            {
                'command': 'volume_up',
                'parameter': {
                    'uid': uid.lower(),
                    'group_command': group_command,
                }
            }
        )

    def volumedown(self, uid, group_command):
        return self.send(
            {
                'command': 'volume_down',
                'parameter': {
                    'uid': uid.lower(),
                    'group_command': group_command,
                }
            }
        )

    def next(self, uid):
        return self.send(
            {
                'command': 'next',
                'parameter': {
                    'uid': uid.lower(),
                }
            }
        )

    def previous(self, uid):
        return self.send(
            {
                'command': 'previous',
                'parameter': {
                    'uid': uid.lower(),
                }
            }
        )

    def get_maxvolume(self, uid):
        return self.send(
            {
                'command': 'get_max_volume',
                'parameter': {
                    'uid': uid.lower(),
                }
            }
        )

    def set_maxvolume(self, uid, max_volume, group_command):
        return self.send(
            {
                'command': 'set_max_volume',
                'parameter': {
                    'max_volume': max_volume,
                    'uid': uid.lower(),
                    'group_command': group_command,
                }
            }
        )

    def client_list(self):
        return self.send(
            {
                'command': 'client_list'
            }
        )

    def get_trackposition(self, uid, force_refresh):
        return self.send(
            {
                'command': 'get_track_position',
                'parameter': {
                    'uid': uid.lower(),
                    'force_refresh': force_refresh
                }
            }
        )

    def set_trackposition(self, uid, timestamp):
        return self.send(
            {
                'command': 'set_track_position',
                'parameter': {
                    'uid': uid.lower(),
                    'timestamp': timestamp
                }
            }
        )

    def get_track_uri(self, uid):
        return self.send(
            {
                'command': 'get_track_uri',
                'parameter': {
                    'uid': uid.lower()
                }
            }
        )

    def get_track_title(self, uid):
        return self.send(
            {
                'command': 'get_track_title',
                'parameter': {
                    'uid': uid.lower()
                }
            }
        )

    def get_track_artist(self, uid):
        return self.send(
            {
                'command': 'get_track_artist',
                'parameter': {
                    'uid': uid.lower()
                }
            }
        )

    def get_radio_station(self, uid):
        return self.send(
            {
                'command': 'get_radio_station',
                'parameter': {
                    'uid': uid.lower()
                }
            }
        )

    def get_radio_show(self, uid):
        return self.send(
            {
                'command': 'get_radio_show',
                'parameter': {
                    'uid': uid.lower()
                }
            }
        )

    def play_url(self, uid, url):
        return self.send(
            {
                'command': 'play_uri',
                'parameter': {
                    'uid': uid.lower(),
                    'uri': url
                }
            }
        )

    def play_snippet(self, uid, url, volume, fade_in, group_command):
        return self.send(
            {
                'command': 'play_snippet',
                'parameter': {
                    'uid': uid.lower(),
                    'uri': url,
                    'volume': volume,
                    'fade_in': fade_in,
                    'group_command': group_command
                }
            }
        )

    def play_tts(self, uid, tts, volume, language, fade_in, force_stream_mode, group_command):
        return self.send(
            {
                'command': 'play_tts',
                'parameter': {
                    'uid': uid.lower(),
                    'tts': tts,
                    'volume': volume,
                    'fade_in': fade_in,
                    'group_command': group_command,
                    'force_stream_mode': force_stream_mode,
                    'language': language
                }
            }
        )

    def is_coordinator(self, uid):
        return self.send(
            {
                'command': 'is_coordinator',
                'parameter': {
                    'uid': uid.lower(),
                }
            }
        )

    def tts_local_mode(self, uid):
        return self.send(
            {
                'command': 'tts_local_mode',
                'parameter': {
                    'uid': uid.lower(),
                }
            }
        )

    def get_playlist(self, uid):
        return self.send(
            {
                'command': 'get_playlist',
                'parameter': {
                    'uid': uid.lower(),
                }
            }
        )

    def set_playlist(self, uid, playlist):
        return self.send(
            {
                'command': 'set_playlist',
                'parameter': {
                    'uid': uid.lower(),
                    'playlist': playlist
                }
            }
        )


if __name__ == '__main__':
    # client_ip = "192.168.178.53"
    # client_port = 5005
    # server_ip = "192.168.178.53"
    # server_port = "12900"
    # cmd = SonosBrokerCmd(client_ip, client_port, server_ip, server_port)
    broker_cmd = SonosBrokerCmd()
    broker_cmd.cmdloop()