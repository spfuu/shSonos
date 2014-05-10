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
from lib_sonos.utils import really_utf8, really_unicode
import socket
import select
import re
import logging
from time import sleep
from http.client import HTTPConnection
from soco import SoCo, discover

try:
    import xml.etree.cElementTree as XML
except ImportError:
    import xml.etree.ElementTree as XML

NS = {
    'r': 'urn:schemas-rinconnetworks-com:metadata-1-0/',
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


# noinspection PyProtectedMember
class SonosServerService():

    _sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    _sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    def __init__(self, host, port, smb_url, local_share, quota, tts_enabled):
        self.host = host
        self.port = port
        self.smb_url = smb_url
        self.local_share = local_share
        self.quota = quota
        self.tts_enabled =tts_enabled
        threading.Thread(target=self.get_speakers_periodically).start()

    def get_speakers_periodically(self):

        events = ['/MediaRenderer/RenderingControl/Event', '/MediaRenderer/AVTransport/Event']

        #in seconds
        sleep_scan = 30

        #new devices will always be deep scanned, old speaker every 10 loops
        max_sleep_count = 10

        deep_scan_count = 0

        while 1:
            print('scan devices ...')
            active_uids = []

            for soco_speaker in discover():
                uid = soco_speaker.speaker_info['uid'].lower()
                active_uids.append(uid)

                #new speaker found, update it
                if uid not in sonos_speaker.sonos_speakers:

                    soco_speaker.get_speaker_info(refresh=True)
                    sonos_speaker.sonos_speakers[uid] = SonosSpeaker(soco_speaker)

                    for event in events:
                        self.subscribe_speaker_event(sonos_speaker.sonos_speakers[uid], event, self.host, self.port,
                                                     sleep_scan * max_sleep_count * 2)
                #speaker already in list, update only when deep scan is forced
                else:
                    if deep_scan_count == max_sleep_count:
                        sonos_speaker.sonos_speakers[uid].soco.get_speaker_info(refresh=True)

                        for event in events:
                            self.unsubscribe_speaker_event(sonos_speaker.sonos_speakers[uid], event,
                                                       sonos_speaker.sonos_speakers[uid].subscription, self.host, self.port)
                            self.subscribe_speaker_event(sonos_speaker.sonos_speakers[uid], event, self.host, self.port,
                                                     sleep_scan * max_sleep_count * 2)

            offline_uids = set(list(sonos_speaker.sonos_speakers.keys())) - set(active_uids)

            for uid in offline_uids:
                print("offline speaker: {} -- removing from list".format(uid))
                sonos_speaker.sonos_speakers[uid].set_online_status(False)
                sonos_speaker.sonos_speakers[uid].send_data()
                del sonos_speaker.sonos_speakers[uid]

            deep_scan_count += 1
            sleep(sleep_scan)

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

            if not dom:
                return

            node = dom.getElementsByTagName('LastChange')
            if node:

                #fetching Event node
                event_string = really_unicode(node[0].firstChild.nodeValue)
                dom = XML.fromstring(event_string)

                if not dom:
                    return None

                for namespace, method in parse_methods.items():
                    element = dom.find("./%sInstanceID" % namespace)
                    if element:
                        method(uid, dom, namespace)

            if uid in sonos_speaker.sonos_speakers:
                sonos_speaker.sonos_speakers[uid].send_data()

        except Exception as err:
            print(err)
            return None

    def parse_mediarenderer_avtransport_event(self, uid, dom, namespace):

        if uid not in sonos_speaker.sonos_speakers:
            return

        track_uri_element = dom.find(".//%sCurrentTrackURI" % namespace)
        if track_uri_element is not None:
            track_uri = track_uri_element.get('val')

        sonos_speaker.sonos_speakers[uid]._track_uri(track_uri)

        #check whether radio or mp3 is played ---> CurrentTrackDuration > 0 is mp3
        track_duration_element = dom.find(".//%sCurrentTrackDuration" % namespace)
        if track_duration_element is not None:
            track_duration = track_duration_element.get('val')
            if track_duration:
                sonos_speaker.sonos_speakers[uid]._track_duration(track_duration)

                if track_duration == '0:00:00':
                    sonos_speaker.sonos_speakers[uid]._track_position("00:00:00")
                    sonos_speaker.sonos_speakers[uid]._streamtype("radio")
                else:
                    sonos_speaker.sonos_speakers[uid]._streamtype("music")
            else:
                sonos_speaker.sonos_speakers[uid]._track_duration("00:00:00")

        transport_state_element = dom.find(".//%sTransportState" % namespace)
        if transport_state_element is not None:
            transport_state = transport_state_element.get('val')

            if transport_state:

                if transport_state.lower() == "transitioning":
                    #because where is no event for current track position, we call it active
                    sonos_speaker.sonos_speakers[uid].get_track_info()

                if transport_state.lower() == "stopped":
                    sonos_speaker.sonos_speakers[uid]._stop(1)
                    sonos_speaker.sonos_speakers[uid]._play(0)
                    sonos_speaker.sonos_speakers[uid]._pause(0)

                if transport_state.lower() == "paused_playback":
                    sonos_speaker.sonos_speakers[uid]._stop(0)
                    sonos_speaker.sonos_speakers[uid]._play(0)
                    sonos_speaker.sonos_speakers[uid]._pause(1)

                if transport_state.lower() == "playing":
                    sonos_speaker.sonos_speakers[uid]._stop(0)
                    sonos_speaker.sonos_speakers[uid]._play(1)
                    sonos_speaker.sonos_speakers[uid]._pause(0)

                    #get current track info, if new track is played or resumed to get track_uri, track_album_art
                    sonos_speaker.sonos_speakers[uid].get_track_info()


        didl_element = dom.find(".//%sCurrentTrackMetaData" % namespace)
        if didl_element is not None:
            didl = didl_element.get('val')
            if didl:
                didl_dom = XML.fromstring(didl)
                if didl_dom:
                    self.parse_track_metadata(uid, didl_dom)

        if sonos_speaker.sonos_speakers[uid].streamtype == 'radio':
             r_namespace = '{urn:schemas-rinconnetworks-com:metadata-1-0/}'
             enqueued_data = dom.find(".//%sEnqueuedTransportURIMetaData" % r_namespace)
             if enqueued_data is not None:
                enqueued_data = enqueued_data.get('val')
                sonos_speaker.sonos_speakers[uid].metadata = enqueued_data
                dom = XML.fromstring(enqueued_data)

                if dom:
                    SonosServerService.parse_radio_mediadata(uid, dom)

    @staticmethod
    def parse_mediarenderer_renderingontrol_event(uid, dom, namespace):

        volume_state_element = dom.find(".//%sVolume[@channel='Master']" % namespace)
        if volume_state_element is not None:
            volume = volume_state_element.get('val')
            if volume:
                sonos_speaker.sonos_speakers[uid]._volume(volume)

        mute_state_element = dom.find(".//%sMute[@channel='Master']" % namespace)
        if mute_state_element is not None:
            mute = mute_state_element.get('val')
            if mute:
                sonos_speaker.sonos_speakers[uid]._mute(mute)

    #radio exclusive data
    @staticmethod
    def parse_radio_mediadata(uid, dom):

        radio_station = ''

        radio_station_element = dom.find('.//dc:title', NS)

        if radio_station_element is not None:
            radio_station = radio_station_element.text

        sonos_speaker.sonos_speakers[uid]._radio_station(radio_station)

    @staticmethod
    def parse_track_metadata(uid, dom):

        ignore_title_string = ('ZPSTR_BUFFERING', 'ZPSTR_BUFFERING', 'ZPSTR_CONNECTING', 'x-sonosapi-stream')

        title = ''
        artist = ''

        try:
            #title listening radio
            stream_content_element = dom.find('.//r:streamContent', NS)
            if stream_content_element is not None:
                stream_content = stream_content_element.text
                if stream_content:
                    if not stream_content.startswith(ignore_title_string):
                        #if radio, in most cases the following format is used: artist - title
                        #if stream_content is not null, radio is assumed
                        split_title = stream_content.split('-')

                        if split_title:
                            if len(split_title)==1:
                                title = split_title

                            if len(split_title) == 2:
                                artist = split_title[0].strip()
                                title = split_title[1].strip()

                            # mostly this happens during commercial breaks, news, weather etc
                            if len(split_title) > 2:
                                artist = split_title[0].strip()
                                title = '-'.join(split_title[1:])
                        else:
                            title = stream_content

            radio_show_element = dom.find('.//r:radioShowMd', NS)
            if radio_show_element is not None:
                radio_show = radio_show_element.text
                if radio_show:
                    #the foramt of a radio_shw item seems to be this format:
                    # <radioshow><,p123456> --> rstrip ,p....
                    radio_show = radio_show.split(',p', 1)

                    if len(radio_show) > 1:
                        radio_show = radio_show[0]
                else:
                    radio_show = ''

                sonos_speaker.sonos_speakers[uid]._radio_show(radio_show)

            album_art = dom.findtext('.//{urn:schemas-upnp-org:metadata-1-0/upnp/}albumArtURI')
            if album_art:
                if not album_art.startswith(('http:', 'https:')):
                    album_art = 'http://' + sonos_speaker.sonos_speakers[uid].ip + ':1400' + album_art
                sonos_speaker.sonos_speakers[uid]._track_album_art(album_art)

            #mp3, etc -> overrides stream content
            title_element = dom.find('.//dc:title', NS)
            if title_element is not None:
                assumed_title = title_element.text
                if assumed_title:
                    if not assumed_title.startswith(ignore_title_string):
                        title = assumed_title

            artist_element = dom.find('.//dc:creator', NS)
            if artist_element is not None:
                assumed_artist = artist_element.text
                if assumed_artist:
                    artist = assumed_artist

            if not artist:
                artist = ''
            if not title:
                title = ''

            sonos_speaker.sonos_speakers[uid]._track_artist(artist.title())
            sonos_speaker.sonos_speakers[uid]._track_title(title.title())

        except Exception as err:
            print(err)