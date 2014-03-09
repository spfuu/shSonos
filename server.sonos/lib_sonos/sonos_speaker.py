# -*- coding: utf-8 -*-
import threading
import time
import json
import xml
from soco.core import SoCo
from lib_sonos import udp_broker

try:
    import xml.etree.cElementTree as XML
except ImportError:
    import xml.etree.ElementTree as XML

sonos_speakers = {}

class SonosSpeaker():
    def __init__(self):
        self.metadata = ''
        self.uid = ''
        self.ip = ''
        self.model = ''
        self.zone_name = ''
        self.zone_icon = ''
        self.serial_number = ''
        self.software_version = ''
        self.hardware_version = ''
        self.mac_address = ''
        self.streamtype = ''
        self.volume = 0
        self.mute = 0
        self.led = 1
        self.stop = False
        self.play = False
        self.pause = False
        self.track_title = "No track title"
        self.track_artist = "No track artist"
        self.track_duration = "00:00:00"
        self.track_position = "00:00:00"
        self.playlist_position = 0
        self.track_uri = ''
        self.track_album_art = ''
        self.radio_show = ''
        self.radio_station =''

    def to_JSON(self):
        to_ignore = ['metadata', 'subscription']
        json_dict= dict(self.__dict__)

        for value in to_ignore:
            if value in json_dict:
                del json_dict[value]
        return json.dumps(self, default=lambda o: json_dict, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': '))

    def __dir__(self):
        return ['uid', 'ip', 'model', 'zone_name', 'zone_icon', 'serial_number', 'software_version',
                'hardware_version', 'mac_address', 'id', 'status']

    def get_soco(self):
        return SoCo(self.ip)

    def set_volume(self, volume):
        volume = int(volume)
        SonosSpeaker.check_volume_range(volume)
        soco = self.get_soco()
        soco.volume = volume
        self.volume = volume

    def get_volume(self):
        soco = self.get_soco()
        self.volume = soco.volume

    def set_stop(self, value):
        if value:
            soco = self.get_soco()
            soco.stop()
            self.stop = 1
            self.play = 0
            self.pause = 0
        else:
            self.set_play(True)

    def set_play(self, value):
        if value:
            soco = self.get_soco()
            soco.play()
            self.stop = 0
            self.play = 1
            self.pause = 0
        else:
            self.set_pause(True)

    def set_pause(self, value):
        if value:
            soco = self.get_soco()
            soco.pause()
            self.stop = 0
            self.play = 0
            self.pause = 1
        else:
            self.set_play(True)

    def set_mute(self, value):
        soco = self.get_soco()
        soco.mute = value
        self.mute = int(value)

    def get_mute(self):
        soco = self.get_soco()
        self.mute = soco.mute

    def set_led(self, value):
        soco = self.get_soco()
        soco.status_light = value
        self.led = int(value)

    def get_led(self):
        soco = self.get_soco()
        self.led = soco.status_light

    def set_next(self):
        soco = self.get_soco()
        soco.next()

    def set_previous(self):
        soco = self.get_soco()
        soco.previous()

    def set_seek(self, timestamp):
        soco = self.get_soco()
        soco.seek(timestamp)

    def get_track_info(self):
        soco = self.get_soco()
        track_info = soco.get_current_track_info()
        self._track_position(track_info['position'])
        self._playlist_position(track_info['playlist_position'])

        #self._track_duration(track_info['duration'])
        #self._tack_uri(track_info['uri'])
        #self._track_album_art(track_info['album_art'])
        #self._track_title(track_info['title'])
        #self._track_artist(track_info['artist'])

    def set_play_uri(self, uri):
        soco = self.get_soco()
        soco.play_uri(uri)

    def set_play_snippet(self, uri, volume):
        #we use the sleep function, so thread it !!
        t = threading.Thread(target=self._play_snippet_thread, args=(uri, volume))
        t.start()

    def set_add_to_queue(self, uri):
        soco = self.get_soco()
        soco.add_to_queue(uri)

    def send_data(self):
        data = self.to_JSON()
        udp_broker.UdpBroker.udp_send(data)

######### internal methods #######################################

    def _play_snippet_thread(self, uri, volume):

        if self.play:
            self.get_track_info()
            queued_streamtype =self.streamtype
            queued_uri = self.track_uri
            queued_playlist_position = self.playlist_position
            queued_track_position = self.track_position
            queued_metadata = self.metadata

        queued_volume = self.volume

        self._fadedown_volume()
        self.set_volume(volume)
        self.set_play_uri(uri)
        self.get_track_info()

        h, m, s = self.track_duration.split(":")
        seconds = int(h)*3600+int(m)*60+int(s)
        time.sleep(seconds)

        #something changed during playing the audio snippet. Maybe there was command send by an other client (iPad e.g)
        if self.track_uri != uri:
            return

        self.set_volume(0)

        if queued_playlist_position:
            soco = self.get_soco()

            if queued_streamtype == "music":
                soco.play_from_queue(int(queued_playlist_position)-1)
                soco.seek(queued_track_position)
            else:
                soco.play_uri(queued_uri, queued_metadata)

            self._fadeup_volume(queued_volume)

        else:
            self.set_volume(queued_volume)

    def _fadedown_volume(self):
        #fade volume to zero in 7 steps
        steps = 7
        step = (self.volume + steps // 2) // steps

        if steps > 0:
            counter = 0 #max loop in case of failure or manipulated volume by another client
            while self.volume > step and counter < steps:
                self.set_volume(self.volume-step)
                counter += 1

        self.set_volume(0)

    def _fadeup_volume(self, volume_to_reach):
        #fade volume up in 7 steps
        steps = 7
        step = (volume_to_reach + steps // 2) // steps

        if step > 0:
            while self.volume < volume_to_reach:
                volume_to_set = self.volume + step
                if  volume_to_set <= volume_to_reach:
                    self.set_volume(volume_to_set)
                else:
                    self.set_volume(volume_to_reach)
        else:
            self.set_volume(volume_to_reach)

    def _streamtype(self, value):
        if value != 'radio':
            self.radio_station = ''
            self.radio_show = ''
        self.streamtype = value

    def _mute(self, value):
        self.mute = int(value);

    def _volume(self, value):
        self.volume = int(value)

    def _play(self, value):
        self.play = int(value)

    def _pause(self, value):
        self.pause = int(value)

    def _stop(self, value):
        self.stop = int(value)

    def _track_album_art(self, track_album_art):
        self.track_album_art = track_album_art

    def _track_uri(self, track_uri):
        self.track_uri = track_uri

    def _track_duration(self, track_duration):
        if not track_duration:
            track_duration = "00:00:00"
        self.track_duration = track_duration

    def _track_position(self, track_position):
        if not track_position:
            track_position = "00:00:00"
        self.track_position = track_position

    def _track_title(self, track_title):
        if not track_title:
            track_title = ''
        self.track_title = track_title

    def _track_artist(self, track_artist):
        if not track_artist:
            track_artist = ''
        self.track_artist = track_artist

    def _playlist_position(self, playlist_position):
        self.playlist_position  = playlist_position

    def _tack_uri(self, track_uri):
        self.track_uri = track_uri

    def _radio_show(self, radio_show):
        self.radio_show = radio_show

    def _radio_station(self, radio_station):
        self.radio_station = radio_station
#######################################################################

    @staticmethod
    def check_volume_range(volume):
        if volume < 0 or volume > 100:
            msg = 'Volume has to be between 0 and 100.'
            raise Exception(msg)
