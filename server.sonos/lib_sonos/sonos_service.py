from __future__ import unicode_literals

# -*- coding: utf-8 -*-
import queue
import requests

__author__ = 'pfischi'

from collections import namedtuple
import threading
from lib_sonos import sonos_speaker
from lib_sonos.sonos_speaker import SonosSpeaker
from lib_sonos.definitions import SCAN_TIMEOUT, RENEW_SUBSCRIPTION_COUNT
import socket
import logging
from time import sleep
from soco import discover
from threading import Lock
from lib_sonos import utils

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
        self.lock = Lock()
        self.host = host
        self.port = port
        self.smb_url = smb_url
        self.local_share = local_share
        self.quota = quota
        self.tts_enabled = tts_enabled
        self.event_queue = queue.Queue()
        threading.Thread(target=self.process_events).start()
        threading.Thread(target=self.get_speakers_periodically).start()

    def get_speakers_periodically(self):

        sleep_scan = SCAN_TIMEOUT
        renew_subscription_timeout = 0

        while 1:
            try:
                renew_subscription_timeout += 1
                print('scan devices ...')

                if renew_subscription_timeout < RENEW_SUBSCRIPTION_COUNT:
                    self.discover(renew_subscription=False)
                else:
                    renew_subscription_timeout = 0
                    print('Renewing event subscriptions ...')
                    self.discover(renew_subscription=True)

            except Exception as err:
                print(err)
            finally:
                sleep(sleep_scan)

    def discover(self, renew_subscription=False):
        try:
            self.lock.acquire()

            active_uids = []

            for soco_speaker in discover():
                uid = soco_speaker.uid.lower()

                #new speaker found, update it
                if uid not in sonos_speaker.sonos_speakers:
                    try:
                        soco_speaker.get_speaker_info(refresh=True)
                        active_uids.append(uid)
                    except Exception as err:
                        #sometimes an offline speaker is cached and will be found by the discover function
                        continue
                    sonos_speaker.sonos_speakers[uid] = SonosSpeaker(soco_speaker)
                    sonos_speaker.sonos_speakers[uid].model = self.get_model_name(sonos_speaker.sonos_speakers[uid].ip)

                else:
                    try:
                        sonos_speaker.sonos_speakers[uid].soco.get_speaker_info(refresh=True)
                        active_uids.append(uid)
                    except Exception:
                        continue

                sonos_speaker.sonos_speakers[uid].event_subscription(self.event_queue, renew_subscription)

            offline_uids = set(list(sonos_speaker.sonos_speakers.keys())) - set(active_uids)

            for uid in offline_uids:
                print("offline speaker: {} -- removing from list".format(uid))
                sonos_speaker.sonos_speakers[uid].status = False
                sonos_speaker.sonos_speakers[uid].send_data()
                del sonos_speaker.sonos_speakers[uid]

            #add the sonos master speaker to all slaves in the group
            for speaker in sonos_speaker.sonos_speakers.values():
                coordinator_uid = speaker.soco.group.coordinator.uid.lower()

                if coordinator_uid != speaker.uid:
                    sonos_speaker.sonos_speakers[speaker.uid].speaker_zone_coordinator = sonos_speaker.sonos_speakers[coordinator_uid]
                else:
                    sonos_speaker.sonos_speakers[speaker.uid].speaker_zone_coordinator = None

                #reset members
                sonos_speaker.sonos_speakers[speaker.uid].additional_zone_members = []

                for member in speaker.soco.group.members:
                    member_uid = member.uid.lower()
                    if member_uid != speaker.uid:
                        sonos_speaker.sonos_speakers[speaker.uid].additional_zone_members.append(sonos_speaker.sonos_speakers[member_uid])

        except Exception as err:
            print('Error in method discover()!\nError: {}'.format(err))
        finally:
            self.lock.release()

    def process_events(self):
        while True:
            try:

                event = self.event_queue.get()
                if event[2] is None:
                    return

                uid = event[0].lower().rsplit('_sub', 1)

                if not uid:
                    print("No a valid event subscription id: {}".format(event[0].lower()))
                    return

                uid = uid[0]
                uid = uid.rsplit('uuid:', 1)

                if not uid:
                    print("No a valid event subscription id: {}".format(event[0].lower()))
                    return

                uid = uid[1]

                if uid not in sonos_speaker.sonos_speakers:
                    print("No sonos speaker found for subscription {}".format(event[0].lower()))
                    continue

                speaker = sonos_speaker.sonos_speakers[uid]

                if event[2].service_type == 'ZoneGroupTopology':
                    #we're using the soco framework to discover new topology
                    #this is a bit of network traffic overhead, but we don't nedd to do the same work
                    self.discover()

                if event[2].service_type == 'AVTransport':
                    self.handle_AVTransport_event(speaker, event[3])

                if event[2].service_type == 'RenderingControl':
                    self.handle_RenderingControl_event(speaker, event[3])

                speaker.send_data()

            except queue.Empty:
                pass
            except KeyboardInterrupt:
                break
            finally:
                self.event_queue.task_done()

    #missing model name, not implemented in soco framework
    def get_model_name(self, ip):

        response = requests.get('http://' + ip + ':1400/xml/device_description.xml')
        dom = XML.fromstring(response.content)

        if dom.findtext('.//{urn:schemas-upnp-org:device-1-0}modelName') is not None:
            return dom.findtext('.//{urn:schemas-upnp-org:device-1-0}modelName')

        return ""

    def handle_AVTransport_event(self, speaker, variables):
        namespace = '{urn:schemas-upnp-org:metadata-1-0/AVT/}'
        xml = variables['LastChange']
        dom = XML.fromstring(xml)

############# CURRENT TRACK URI

        track_uri_element = dom.find(".//%sCurrentTrackURI" % namespace)
        if track_uri_element is not None:
            track_uri = track_uri_element.get('val')

        speaker._track_uri = track_uri

############ CURRENT TRACK DURATION

        #check whether radio or mp3 is played ---> CurrentTrackDuration > 0 is mp3
        track_duration_element = dom.find(".//%sCurrentTrackDuration" % namespace)
        if track_duration_element is not None:
            track_duration = track_duration_element.get('val')
            if track_duration:
                speaker._track_duration = track_duration

                if track_duration == '0:00:00':
                    speaker._track_position = "00:00:00"
                    speaker._streamtype = "radio"
                else:
                    speaker._streamtype = "music"
            else:
                speaker._track_duration = "00:00:00"

############ TRANSPORTSTATE

        transport_state_element = dom.find(".//%sTransportState" % namespace)

        if transport_state_element is not None:

            transport_state = transport_state_element.get('val')

            if transport_state:

                if transport_state.lower() == "transitioning":
                    #because where is no event for current track position, we call it active
                    speaker.track_info()

                #don't use property setter here. This would trigger a soco action. Use class variable instead!
                if transport_state.lower() == "stopped":
                    speaker._stop = 1
                    speaker._play = 0
                    speaker._pause = 0

                if transport_state.lower() == "paused_playback":
                    speaker._stop = 0
                    speaker._play = 0
                    speaker._pause = 1

                if transport_state.lower() == "playing":
                    speaker._stop = 0
                    speaker._play = 1
                    speaker._pause = 0

                    #get current track info, if new track is played or resumed to get track_uri, track_album_art
                    speaker.track_info()

############ CURRENT TRACK METADATA

        didl_element = dom.find(".//%sCurrentTrackMetaData" % namespace)

        if didl_element is not None:
            didl = didl_element.get('val')
            if didl:
                didl_dom = XML.fromstring(didl)
                if didl_dom:
                    self.parse_track_metadata(speaker, didl_dom)

        if speaker.streamtype == 'radio':

            r_namespace = '{urn:schemas-rinconnetworks-com:metadata-1-0/}'
            enqueued_data = dom.find(".//%sEnqueuedTransportURIMetaData" % r_namespace)

            if enqueued_data is not None:

                enqueued_data = enqueued_data.get('val')
                speaker._metadata = enqueued_data

                try:
                    radio_dom = XML.fromstring(enqueued_data)

                    if radio_dom:
                        radio_station = ''
                        radio_station_element = radio_dom.find('.//dc:title', NS)

                        if radio_station_element is not None:
                            radio_station = radio_station_element.text

                        speaker._radio_station = radio_station

                except Exception: #raised, if enqued_data is empty
                    speaker._radio_show = ''
                    speaker._radio_station = ''

        else:
            speaker._radio_show = ''
            speaker._radio_station = ''

    def handle_RenderingControl_event(self, speaker, variables):
        namespace = '{urn:schemas-upnp-org:metadata-1-0/RCS/}'
        xml = variables['LastChange']
        dom = XML.fromstring(xml)

        volume_state_element = dom.find(".//%sVolume[@channel='Master']" % namespace)
        if volume_state_element is not None:
            volume = volume_state_element.get('val')

            #don't use property setter here. This would trigger a soco action. Use class variable instead!
            if volume:
                if utils.check_max_volume_exceeded(volume, speaker.max_volume):
                    speaker.volume = speaker.max_volume
                else:
                    speaker._volume = volume

        mute_state_element = dom.find(".//%sMute[@channel='Master']" % namespace)
        if mute_state_element is not None:
            mute = mute_state_element.get('val')

            #don't use property setter here. This would trigger a soco action. Use class variable instead!
            if mute:
                speaker._mute = int(mute)

    @staticmethod
    def parse_track_metadata(speaker, dom):

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
                            if len(split_title) == 1:
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
                    #the foramt of a radio_show item seems to be this format:
                    # <radioshow><,p123456> --> rstrip ,p....
                    radio_show = radio_show.split(',p', 1)

                    if len(radio_show) > 1:
                        radio_show = radio_show[0]
                else:
                    radio_show = ''

                speaker._radio_show = radio_show

            album_art = dom.findtext('.//{urn:schemas-upnp-org:metadata-1-0/upnp/}albumArtURI')
            if album_art:
                if not album_art.startswith(('http:', 'https:')):
                    album_art = 'http://' + speaker.ip + ':1400' + album_art
                speaker._track_album_art = album_art

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

            speaker._track_artist = artist
            speaker._track_title = title

        except Exception as err:
            print(err)