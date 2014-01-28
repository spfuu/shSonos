# -*- coding: utf-8 -*-
__author__ = 'pfischi'


sonos_speakers = {}

class SonosSpeaker():
    def __init__(self):
        self.uid = ''
        self.ip = ''
        self.model = ''
        self.zone_name = ''
        self.zone_icon = ''
        self.serial_number = ''
        self.software_version = ''
        self.hardware_version = ''
        self.mac_address = ''
        self.id = None
        self.status = 0
        self.streamtype = ''
        self.volume = 0
        self.mute = 0
        self.led = 1
        self.streamtype = "No streamtype"
        self.stop = False
        self.play = False
        self.pause = False
        self.track = "No track title"
        self.artist = "No track artist"

    def __dir__(self):
        return ['uid', 'ip', 'model', 'zone_name', 'zone_icon', 'serial_number', 'software_version',
                'hardware_version', 'mac_address', 'id', 'status']