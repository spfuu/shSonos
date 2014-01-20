# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from xml.dom import minidom
from udp_broker import UdpBroker
from collections import namedtuple
import threading
import requests
from soco.core import SoCo
from utils import really_unicode, really_utf8, prettify
import socket
import select
import definitions
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

    def __dir__(self):
        return ['uid', 'ip', 'model', 'zone_name', 'zone_icon', 'serial_number', 'software_version',
                'hardware_version', 'mac_address', 'id', 'status']


class SonosServerService():
    def __init__(self, host, port):

        self.udp_broker = UdpBroker()
        self.host = host
        self.port = port
        self.speakers = {}

        self._sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
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
                self.speakers = {}
                deep_scan_count = 0
            else:
                "find any newly added speaker"
                new_uids = set(new_speakers) - set(self.speakers)

            #do a deep scn for all new devices
            for uid in new_uids:
                print('new speaker: {} -- adding to list'.format(uid))
                #add the new speaker to our main list
                speaker = self.get_speaker_info(new_speakers[uid])
                self.speakers[speaker.uid] = speaker

                for event in events:
                    self.subscribe_speaker_event(speaker, event, self.host, self.port, sleep_scan * max_sleep_count * 2)

            #find all offline speaker
            offline_uids = set(self.speakers) - set(new_speakers)

            for u in offline_uids:
                print("offline speaker: {} -- removing from list".format(u))

            if deep_scan_count == max_sleep_count:
                print("Performing deep scan for speakers ...")

                for uid, speaker in self.speakers.items():
                    deep_scan_count = 0
                    speaker = self.get_speaker_info(self.speakers[speaker.uid])
                    #re-subscribe

                    for event in events:
                        self.unsubscribe_speaker_event(speaker, event, speaker.subscription, self.host, self.port)
                        self.subscribe_speaker_event(speaker, event, self.host, self.port,
                                                     sleep_scan * max_sleep_count * 2)
                    self.speakers[speaker.uid] = speaker

            deep_scan_count += 1

            sleep(sleep_scan)

    def get_soco(self, uid):
        speaker = self.speakers[uid.lower()]
        if speaker:
            return SoCo(speaker.ip)
        return None

    def get_speakers(self):
        """ Get a list of ips for Sonos devices that can be controlled """
        speakers = {}
        self._sock.sendto(really_utf8(definitions.PLAYER_SEARCH), (definitions.MCAST_GRP, definitions.MCAST_PORT))

        while True:
            response, _, _ = select.select([self._sock], [], [], 1)
            if response:
                data, addr = self._sock.recvfrom(2048)
                # Look for the model in parentheses in a line like this
                # SERVER: Linux UPnP/1.0 Sonos/22.0-65180 (ZPS5)
                searchmodel = re.search(definitions.model_pattern, data)
                searchuid = re.search(definitions.uid_pattern, data)
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

        print(response.text)
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
        print(response)
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

            print(data)
            self.udp_broker.udp_send(data)

        except Exception as err:
            print(err)
            return None


    def parse_mediarenderer_avtransport_event(self, uid, dom, namespace):

        changed_values = []

        #check whether radio or mp3 is played ---> CurrentTrackDuration > 0 is mp3
        track_duration_element = dom.find(".//%sCurrentTrackDuration" % namespace)
        if track_duration_element is not None:
            track_duration = track_duration_element.get('val')
            if track_duration:
                if track_duration == '0:00:00':
                    changed_values.append("speaker/{}/streamtype/radio".format(uid))
                else:
                    changed_values.append("speaker/{}/streamtype/music".format(uid))




        transport_state_element = dom.find(".//%sTransportState" % namespace)
        if transport_state_element is not None:
            transport_state = transport_state_element.get('val')

            if transport_state:
                if transport_state.lower() == "stopped":
                    changed_values.append("speaker/{}/stop/1".format(uid))
                    changed_values.append("speaker/{}/play/0".format(uid))
                    changed_values.append("speaker/{}/pause/0".format(uid))
                if transport_state.lower() == "paused_playback":
                    changed_values.append("speaker/{}/stop/0".format(uid))
                    changed_values.append("speaker/{}/play/0".format(uid))
                    changed_values.append("speaker/{}/pause/1".format(uid))
                if transport_state.lower() == "playing":
                    changed_values.append("speaker/{}/stop/0".format(uid))
                    changed_values.append("speaker/{}/play/1".format(uid))
                    changed_values.append("speaker/{}/pause/0".format(uid))

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
                changed_values.append("speaker/{}/volume/{}".format(uid, volume))

        mute_state_element = dom.find(".//%sMute[@channel='Master']" % namespace)
        if mute_state_element is not None:
            mute = mute_state_element.get('val')
            if mute:
                changed_values.append("speaker/{}/mute/{}".format(uid, mute))

        return changed_values

    @staticmethod
    def parse_track_metadata(uid, dom):

        namespaces = {'r': 'urn:schemas-rinconnetworks-com:metadata-1-0/', 'dc': 'http://purl.org/dc/elements/1.1/'}

        changed_values = []

        ignore_title_string = ('ZPSTR_BUFFERING', 'ZPSTR_BUFFERING', 'ZPSTR_CONNECTING', 'x-sonosapi-stream')
        #EnqueuedTransportURIMetaData

        title_found = False

        try:
            #title listening radio
            stream_content_element = dom.find('.//r:streamContent', namespaces)
            if stream_content_element is not None:
                stream_content = stream_content_element.text
                if stream_content:
                    if not stream_content.startswith(ignore_title_string):
                        changed_values.append("speaker/{}/track/{}".format(uid, stream_content))
                        title_found = True

            #mp3, etc
            title_element = dom.find('.//dc:title', namespaces)
            if title_element is not None:
                title = title_element.text
                if title:
                    if not title.startswith(ignore_title_string):
                        changed_values.append("speaker/{}/track/{}".format(uid, title))
                        title_found = True

            if not title_found:
                changed_values.append("speaker/{}/track/No track title".format(uid))

        except Exception as err:
            print(err)

        return changed_values



