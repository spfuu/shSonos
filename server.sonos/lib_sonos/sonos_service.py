from __future__ import unicode_literals

# -*- coding: utf-8 -*-
__author__ = 'pfischi'

from xml.dom import minidom
from collections import namedtuple
import threading
import requests
from lib_sonos import sonos_speaker
from lib_sonos.sonos_speaker import SonosSpeaker
from lib_sonos.definitions import uid_pattern, model_pattern, MCAST_PORT, MCAST_GRP, PLAYER_SEARCH
from lib_sonos.udp_broker import UdpBroker, UdpResponse
from lib_sonos.utils import really_utf8, really_unicode
from soco.core import SoCo
import socket
import select
import re
import logging
from time import sleep
from http.client import HTTPConnection

try:
    import xml.etree.cElementTree as XML
except ImportError:
    import xml.etree.ElementTree as XML

NS = {
    'dc': 'http://purl.org/dc/elements/1.1/',
    'upnp': 'urn:schemas-upnp-org:metadata-1-0/upnp/',
    '': 'urn:schemas-upnp-org:metadata-1-0/AVT/',
}
# Register all name spaces within the XML module
for key_, value_ in NS.items():
    XML.register_namespace(key_, value_)

log = logging.getLogger(__name__)
Argument = namedtuple('Argument', 'name, vartype')
Action = namedtuple('Action', 'name, in_args, out_args')

#import sys
#sys.path.append('/usr/smarthome/plugins/sonos/server/pycharm-debug-py3k.egg')
#import pydevd

class SonosServerService():

    _sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    _sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    def __init__(self, host, port):

        self.udp_broker = UdpBroker()
        self.host = host
        self.port = port


        threading.Thread(target=self.get_speakers_periodically).start()

    def get_speakers_periodically(self):

        events = ['/MediaRenderer/RenderingControl/Event', '/MediaRenderer/AVTransport/Event']
        sleep_scan = 10 #in seconds
        max_sleep_count = 10 #new devices will always be deep scanned, old speaker every 10 loops
        deep_scan_count = 0

        while 1:

            new_uids = []
            print('scan devices ...')
            #find all (new and old speaker)
            new_speakers = self.get_speakers()

            if not new_speakers:
                #no speakers found, delete our list
                sonos_speaker.sonos_speakers = {}
                deep_scan_count = 0
            else:
                "find any newly added speaker"
                new_uids = set(new_speakers) - set(sonos_speaker.sonos_speakers)

            #do a deep scn for all new devices
            for uid in new_uids:
                print('new speaker: {} -- adding to list'.format(uid))
                #add the new speaker to our main list
                speaker = self.get_speaker_info(new_speakers[uid])
                sonos_speaker.sonos_speakers[speaker.uid] = speaker

                for event in events:
                    self.subscribe_speaker_event(speaker, event, self.host, self.port, sleep_scan * max_sleep_count * 2)

            #find all offline speaker
            offline_uids = set(sonos_speaker.sonos_speakers) - set(new_speakers)

            for u in offline_uids:
                print("offline speaker: {} -- removing from list".format(u))

            if deep_scan_count == max_sleep_count:
                print("Performing deep scan for speakers ...")

                for uid, speaker in sonos_speaker.sonos_speakers.items():
                    deep_scan_count = 0
                    speaker = self.get_speaker_info(sonos_speaker.sonos_speakers[speaker.uid])
                    #re-subscribe

                    for event in events:
                        self.unsubscribe_speaker_event(speaker, event, speaker.subscription, self.host, self.port)
                        self.subscribe_speaker_event(speaker, event, self.host, self.port,
                                                     sleep_scan * max_sleep_count * 2)
                        sonos_speaker.sonos_speakers[speaker.uid] = speaker

            deep_scan_count += 1

            sleep(sleep_scan)

    @staticmethod
    def get_soco(uid):
        """

        @rtype : soco instance, null if not found
        """
        speaker = sonos_speaker.sonos_speakers[uid.lower()]
        if speaker:
            return SoCo(speaker.ip)
        return None

    @staticmethod
    def get_speakers():
        """ Get a list of ips for Sonos devices that can be controlled """
        speakers = {}
        SonosServerService._sock.sendto(really_utf8(PLAYER_SEARCH), (MCAST_GRP, MCAST_PORT))

        while True:
            response, _, _ = select.select([SonosServerService._sock], [], [], 1)
            if response:
                data, addr = SonosServerService._sock.recvfrom(2048)
                # Look for the model in parentheses in a line like this
                # SERVER: Linux UPnP/1.0 Sonos/22.0-65180 (ZPS5)
                searchmodel = re.search(model_pattern, data)
                searchuid = re.search(uid_pattern, data)
                try:
                    model = really_unicode(searchmodel.group(1))
                    uid = really_unicode(searchuid.group(1))
                except AttributeError:
                    model = None
                    uid = None

                # BR100 = Sonos Bridge,        ZPS3 = Zone Player 3
                # ZP120 = Zone Player Amp 120, ZPS5 = Zone Player 5
                # ZP90  = Sonos Connect,       ZPS1 = Zone Player 1
                # If it's the bridge, then it's not a speaker and shouldn't
                # be returned
                if (model and model != "BR100"):
                    speaker = SonosSpeaker()
                    speaker.uid = uid.lower()
                    speaker.ip = addr[0]
                    speaker.model = model
                    speakers[speaker.uid] = speaker
            else:
                break
        return speakers

    @staticmethod
    def get_speaker_info(speaker):

        """ Get information about the Sonos speaker.
        Returns:
        Information about the Sonos speaker, such as the UID, MAC Address, and
        Zone Name.

        """
        response = requests.get('http://' + speaker.ip + ':1400/status/zp')
        dom = XML.fromstring(response.content)

        if dom.findtext('.//ZoneName') is not None:
            speaker.zone_name = dom.findtext('.//ZoneName')
            speaker.zone_icon = dom.findtext('.//ZoneIcon')
            speaker.uid = dom.findtext('.//LocalUID').lower()
            speaker.serial_number = dom.findtext('.//SerialNumber')
            speaker.software_version = dom.findtext('.//SoftwareVersion')
            speaker.hardware_version = dom.findtext('.//HardwareVersion')
            speaker.mac_address = dom.findtext('.//MACAddress')
            return speaker

    @staticmethod
    def subscribe_speaker_event(speaker, event, host, port, timeout):

        print("speaker {} (ip {}): registering event '{}' to: {}:{}".format(speaker.uid, speaker.ip, event, host,
                                                                            port))

        headers = {'CALLBACK': '<http://{}:{}>'.format(host, port), 'NT': 'upnp:event',
                   'TIMEOUT': 'Second-{}'.format(timeout)}
        conn = HTTPConnection("{}:1400".format(speaker.ip))
        conn.request("SUBSCRIBE", "{}".format(event), "", headers)

        response = conn.getresponse()
        speaker.subscription = response.headers['SID']
        conn.close()

    @staticmethod
    def unsubscribe_speaker_event(speaker, event, sid, host, port):

        print("speaker {} (ip {}): un-registering event '{}' from: {}:{}".format(speaker.uid, speaker.ip, event,
                                                                                 host, port))

        headers = {'SID': '{}'.format(sid)}
        conn = HTTPConnection("{}:1400".format(speaker.ip))
        conn.request("UNSUBSCRIBE", "{}".format(event), "", headers)

        response = conn.getresponse()
        conn.close()

    def response_parser(self, sid, data):

        parse_methods = {'{urn:schemas-upnp-org:metadata-1-0/AVT/}': self.parse_mediarenderer_avtransport_event,
                         '{urn:schemas-upnp-org:metadata-1-0/RCS/}': self.parse_mediarenderer_renderingontrol_event}

        try:
            response_list = []

            #uuid:RINCON_000E58C3892E01400_sub0000000264 --> split uuid: and _sub.....

            uid = sid.lower().rsplit('_sub', 1)

            if not uid:
                print("No speaker found for subscription '{}".format(sid))
                return

            uid = uid[0]
            uid = uid.rsplit('uuid:', 1)

            if not uid:
                print("No speaker found for subscription '{}".format(sid))
                return

            uid = uid[1]

            print("speaker '{} found for subscription '{}".format(uid, sid))

            dom = minidom.parseString(data).documentElement

            #pydevd.settrace('192.168.178.44', port=12000, stdoutToServer=True, stderrToServer=True)

            node = dom.getElementsByTagName('LastChange')
            if node:
                #<LastChange>
                #   <Event>
                #   .....
                #   </Event>
                #</LstChange>

                #fetching Event node
                event_string = really_unicode(node[0].firstChild.nodeValue)
                dom = XML.fromstring(event_string)

                if not dom:
                    return None

                for namespace, method in parse_methods.items():
                    element = dom.find("./%sInstanceID" % namespace)
                    if element is not None:
                        response_list.extend(method(uid, dom, namespace))

            #udp wants a string
            data = ''
            for entry in response_list:
                data = "{}\n{}".format(data, entry)

            UdpBroker.udp_send(data)

        except Exception as err:
            print(err)
            return None

    def parse_mediarenderer_avtransport_event(self, uid, dom, namespace):

        if uid not in sonos_speaker.sonos_speakers:
            return

        changed_values = []

        #check whether radio or mp3 is played ---> CurrentTrackDuration > 0 is mp3
        track_duration_element = dom.find(".//%sCurrentTrackDuration" % namespace)
        if track_duration_element is not None:
            track_duration = track_duration_element.get('val')
            if track_duration:
                sonos_speaker.sonos_speakers[uid].track_duration = track_duration

                if track_duration == '0:00:00':
                    sonos_speaker.sonos_speakers[uid].track_position = "00:00:00"
                    changed_values.append(UdpResponse.track_position(uid))
                    sonos_speaker.sonos_speakers[uid].streamtype = "radio"
                else:
                    sonos_speaker.sonos_speakers[uid].streamtype = "music"

                changed_values.append(UdpResponse.streamtype(uid))

            else:
                sonos_speaker.sonos_speakers[uid].track_duration = "00:00:00"

            changed_values.append(UdpResponse.track_duration(uid))

        transport_state_element = dom.find(".//%sTransportState" % namespace)
        if transport_state_element is not None:
            transport_state = transport_state_element.get('val')

            if transport_state:
                if transport_state.lower() == "transitioning":
                    #because where is no event for current track position, we call it active
                    soco = self.get_soco(uid)
                    track_position = soco.get_current_track_info()['position']

                    if not track_position:
                        track_position = "00:00:00"

                    sonos_speaker.sonos_speakers[uid].track_position = track_position
                    changed_values.append(UdpResponse.track_position(uid))

                if transport_state.lower() == "stopped":
                    sonos_speaker.sonos_speakers[uid].stop = 1
                    sonos_speaker.sonos_speakers[uid].play = 0
                    sonos_speaker.sonos_speakers[uid].pause = 0
                if transport_state.lower() == "paused_playback":
                    sonos_speaker.sonos_speakers[uid].stop = 0
                    sonos_speaker.sonos_speakers[uid].play = 0
                    sonos_speaker.sonos_speakers[uid].pause = 1
                if transport_state.lower() == "playing":
                    sonos_speaker.sonos_speakers[uid].stop = 0
                    sonos_speaker.sonos_speakers[uid].play = 1
                    sonos_speaker.sonos_speakers[uid].pause = 0

                changed_values.append(UdpResponse.stop(uid))
                changed_values.append(UdpResponse.play(uid))
                changed_values.append(UdpResponse.pause(uid))

        didl_element = dom.find(".//%sCurrentTrackMetaData" % namespace)

        if didl_element is not None:
            didl = didl_element.get('val')
            if didl:
                didl_dom = XML.fromstring(didl)
                if didl_dom:
                    changed_values.extend(self.parse_track_metadata(uid, didl_dom))

        return changed_values

    @staticmethod
    def parse_mediarenderer_renderingontrol_event(uid, dom, namespace):

        #changed value in smarthome.py response syntax, change this to your preference
        #e.g. speaker/<uid>/volume/<value>
        """


        @param uid:
        @param dom:
        @rtype : list
        """
        changed_values = []

        volume_state_element = dom.find(".//%sVolume[@channel='Master']" % namespace)
        if volume_state_element is not None:
            volume = volume_state_element.get('val')
            if volume:
                sonos_speaker.sonos_speakers[uid].volume = volume
                changed_values.append(UdpResponse.volume(uid))

        mute_state_element = dom.find(".//%sMute[@channel='Master']" % namespace)
        if mute_state_element is not None:
            mute = mute_state_element.get('val')
            if mute:
                sonos_speaker.sonos_speakers[uid].mute = mute
                changed_values.append(UdpResponse.mute(uid))

        return changed_values

    @staticmethod
    def parse_track_metadata(uid, dom):

        namespaces = {'r': 'urn:schemas-rinconnetworks-com:metadata-1-0/', 'dc': 'http://purl.org/dc/elements/1.1/'}

        changed_values = []

        ignore_title_string = ('ZPSTR_BUFFERING', 'ZPSTR_BUFFERING', 'ZPSTR_CONNECTING', 'x-sonosapi-stream')
        #EnqueuedTransportURIMetaData

        title = ''
        artist = ''

        try:
            #title listening radio
            stream_content_element = dom.find('.//r:streamContent', namespaces)
            if stream_content_element is not None:
                stream_content = stream_content_element.text
                if stream_content:
                    if not stream_content.startswith(ignore_title_string):
                        #if radio, in most cases the following format is used: artist - title
                        #if stream_content is not null, radio is assumed
                        split_title = stream_content.split('-')

                        if split_title:
                            artist = split_title[0].strip()
                            title = split_title[1].strip()
                        else:
                            title = stream_content
            print(title)


            #mp3, etc -> overrides stream content
            title_element = dom.find('.//dc:title', namespaces)
            if title_element is not None:
                assumed_title = title_element.text
                if assumed_title:
                    if not assumed_title.startswith(ignore_title_string):
                        title = assumed_title

            artist_element = dom.find('.//dc:creator', namespaces)
            if artist_element is not None:
                assumed_artist = artist_element.text
                if assumed_artist:
                    artist = assumed_artist

            if not artist:
                artist = "No artist"
            if not title:
                title = "No track title"

            sonos_speaker.sonos_speakers[uid].artist = artist
            sonos_speaker.sonos_speakers[uid].track = title
            changed_values.append(UdpResponse.artist(uid))
            changed_values.append(UdpResponse.track(uid))

        except Exception as err:
            print(err)

        return changed_values

