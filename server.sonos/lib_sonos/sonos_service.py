from __future__ import unicode_literals

# -*- coding: utf-8 -*-
import queue
import requests
from collections import namedtuple
import threading
from lib_sonos import sonos_speaker
from lib_sonos.sonos_speaker import SonosSpeaker
from lib_sonos.definitions import SCAN_TIMEOUT
from lib_sonos.radio_parser import title_artist_parser
import socket
import logging
from time import sleep
from soco import discover
from threading import Lock
from soco.services import zone_group_state_shared_cache
from lib_sonos import utils

try:
    import xml.etree.cElementTree as XML
except ImportError:
    import xml.etree.ElementTree as XML

logger = logging.getLogger('')

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

    def __init__(self, host, port, remote_folder, local_folder, quota, tts_enabled):
        self.event_lock = Lock()
        self.lock = Lock()
        self.host = host
        self.port = port
        self.event_queue = queue.Queue()

        SonosSpeaker.set_tts(local_folder, remote_folder, quota, tts_enabled)

        p_t = threading.Thread(target=self.process_events)
        p_t.daemon = True
        p_t.start()
        g_t = threading.Thread(target=self.get_speakers_periodically)
        g_t.daemon = True
        g_t.start()

    def unsubscribe_speaker_events(self):
        for speaker in sonos_speaker.sonos_speakers.values():
            speaker.event_unsubscribe()

    def get_speakers_periodically(self):

        sleep_scan = SCAN_TIMEOUT

        while 1:
            try:
                logger.debug('active threads: {}'.format(len(threading.enumerate())))
                logger.info('scan devices ...')
                zone_group_state_shared_cache.clear()
                self.discover()

            except Exception as err:
                logger.exception(err)
            finally:
                sleep(sleep_scan)

    def discover(self):
        try:
            with sonos_speaker._sonos_lock:
                zone_group_state_shared_cache.clear()
                active_uids = []
                soco_speakers = discover(timeout=5, include_invisible=False)

                if soco_speakers is None:
                    return

                speaker_to_remove = []

                for soco_speaker in soco_speakers:
                    uid = soco_speaker.uid.lower()

                    # new speaker found, update it
                    if uid not in sonos_speaker.sonos_speakers:
                        try:
                            soco_speaker.get_speaker_info(refresh=True)
                            active_uids.append(uid)
                        except Exception:
                            # !! sometimes an offline speaker is cached and will be found by the discover function
                            speaker_to_remove.append(soco_speaker.uid)
                            continue
                        try:
                            _sp = SonosSpeaker(soco_speaker)
                            sonos_speaker.sonos_speakers[uid] = _sp
                            sonos_speaker.sonos_speakers[uid].model = self.get_model_name(
                                sonos_speaker.sonos_speakers[uid].ip)
                        except Exception:
                            speaker_to_remove.append(soco_speaker.uid)
                            continue  # speaker maybe deleted by another thread
                    else:
                        try:
                            sonos_speaker.sonos_speakers[uid].soco.get_speaker_info(refresh=True)
                            active_uids.append(uid)
                        except Exception:
                            speaker_to_remove.append(soco_speaker.uid)
                            continue  # speaker maybe deleted by another thread

                for uid in speaker_to_remove:
                    uid = uid.lower()
                    if uid in sonos_speaker.sonos_speakers:
                        sonos_speaker.sonos_speakers.pop(uid)

                # remove all offline speakers from internal list #######################################################
                try:
                    offline_uids = set(list(sonos_speaker.sonos_speakers.keys())) - set(active_uids)
                except KeyError:
                    pass  # speaker maybe deleted by another thread

                for uid in offline_uids:
                    logger.info("offline speaker: {uid} -- removing from list".format(uid=uid))
                    try:
                        sonos_speaker.sonos_speakers[uid].status = False
                        sonos_speaker.sonos_speakers[uid].send()
                        del sonos_speaker.sonos_speakers[uid]
                    except KeyError:
                        continue  # speaker maybe deleted by another thread

                # register events for all speaker, this has to be the last step due to some logics in the event ########
                # handling routine #####################################################################################

                for speaker in sonos_speaker.sonos_speakers.values():
                    try:
                        speaker.set_zone_coordinator()
                        speaker.set_group_members()
                        speaker.event_subscription(self.event_queue)
                    except KeyError:
                        pass  # speaker maybe deleted by another thread

        except Exception as err:
            logger.exception('Error in method discover()!\nError: {err}'.format(err=err))
        finally:
            pass

    def process_events(self):
        speakers = []
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

                with sonos_speaker._sonos_lock:
                    try:
                        speaker = sonos_speaker.sonos_speakers[uid]
                        if speaker not in speakers:
                            speakers.append(speaker)
                    except KeyError:
                        pass  # speaker maybe removed from another thread

                if event[2].service_type == 'ZoneGroupTopology':
                    speaker.set_zone_coordinator()
                    speaker.set_group_members()
                    speaker.dirty_music_metadata()

                if event[2].service_type == 'AVTransport':
                    self.handle_AVTransport_event(speaker, event[3])

                if event[2].service_type == 'RenderingControl':
                    self.handle_RenderingControl_event(speaker, event[3])

                if event[2].service_type == 'AlarmClock':
                    self.handle_AlarmClock_event(speaker, event[3])

            except queue.Empty:
                pass
            except KeyboardInterrupt:
                break
            finally:
                self.event_lock.acquire()
                self.event_queue.task_done()
                if not self.event_queue.unfinished_tasks:
                    for speaker in speakers:
                        speaker.send()
                    del speakers[:]
                self.event_lock.release()

    # missing model name, not implemented in soco framework
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

        # ############ CURRENT TRACK URI

        track_uri_element = dom.find(".//%sCurrentTrackURI" % namespace)
        if track_uri_element is not None:
            track_uri = track_uri_element.get('val')

            if track_uri:
                speaker.track_uri = track_uri

        # ########### CURRENT TRACK DURATION

        #check whether radio or mp3 is played ---> CurrentTrackDuration > 0 is mp3
        track_duration_element = dom.find(".//%sCurrentTrackDuration" % namespace)
        if track_duration_element is not None:
            track_duration = track_duration_element.get('val')
            if track_duration:
                speaker.track_duration = track_duration
                if track_duration == '0:00:00':
                    speaker.track_position = "00:00:00"
                    speaker.streamtype = "radio"
                else:
                    speaker.streamtype = "music"
            else:
                speaker.track_duration = "00:00:00"

        ############ CurrentPlayMode

        current_play_mode_element = dom.find(".//%sCurrentPlayMode" % namespace)

        if current_play_mode_element is not None:
            current_play_mode = current_play_mode_element.get('val')
            if current_play_mode:
                speaker.playmode = current_play_mode.lower()

        ############ TRANSPORTSTATE

        transport_state_element = dom.find(".//%sTransportState" % namespace)

        if transport_state_element is not None:

            transport_state = transport_state_element.get('val')

            if transport_state:

                if transport_state.lower() == "transitioning":
                    #because where is no event for current track position, we call it active
                    speaker.get_trackposition(force_refresh=True)

                if transport_state.lower() == "stopped":
                    speaker.stop = 1
                    speaker.play = 0
                    speaker.pause = 0

                if transport_state.lower() == "paused_playback":
                    speaker.stop = 0
                    speaker.play = 0
                    speaker.pause = 1

                if transport_state.lower() == "playing":
                    speaker.stop = 0
                    speaker.play = 1
                    speaker.pause = 0

                    #get current track info, if new track is played or resumed to get track_uri, track_album_art
                    speaker.get_trackposition(force_refresh=True)

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

                        speaker.radio_station = radio_station

                except Exception:  #raised, if enqued_data is empty
                    speaker.radio_show = ''
                    speaker.radio_station = ''
        else:
            speaker.radio_show = ''
            speaker.radio_station = ''

        ############ CURRENT TRACK METADATA

        didl_element = dom.find(".//%sCurrentTrackMetaData" % namespace)

        if didl_element is not None:
            didl = didl_element.get('val')
            if didl:
                didl_dom = XML.fromstring(didl)
                speaker.metadata = didl
                if didl_dom:
                    self.parse_track_metadata(speaker, didl_dom)

    def handle_AlarmClock_event(self, speaker, variables):
        """
        There seems no additional info in variables. The event only gives us the event subscription id.
        So we call the get_alarms routine.
        """
        speaker.get_alarms()

    def handle_RenderingControl_event(self, speaker, variables):
        namespace = '{urn:schemas-upnp-org:metadata-1-0/RCS/}'
        xml = variables['LastChange']
        dom = XML.fromstring(xml)

        volume_state_element = dom.find(".//%sVolume[@channel='Master']" % namespace)
        if volume_state_element is not None:
            volume = volume_state_element.get('val')
            if volume:
                if utils.check_max_volume_exceeded(volume, speaker.max_volume):
                    speaker.set_volume(speaker.max_volume, trigger_action=True)
                else:
                    speaker.volume = int(volume)

        mute_state_element = dom.find(".//%sMute[@channel='Master']" % namespace)
        if mute_state_element is not None:
            mute = mute_state_element.get('val')
            if mute:
                speaker.mute = int(mute)

        bass_state_element = dom.find(".//%sBass" % namespace)
        if bass_state_element is not None:
            bass = bass_state_element.get('val')
            if bass:
                speaker.bass = int(bass)
        treble_state_element = dom.find(".//%sTreble" % namespace)
        if treble_state_element is not None:
            treble = treble_state_element.get('val')
            if treble:
                speaker.treble = int(treble)

        loudness_state_element = dom.find(".//%sLoudness[@channel='Master']" % namespace)
        if loudness_state_element is not None:
            loudness = loudness_state_element.get('val')
            if loudness is not None:
                speaker.loudness = int(loudness)

    @staticmethod
    def parse_track_metadata(speaker, dom):
        ignore_title_string = ('ZPSTR_BUFFERING', 'ZPSTR_BUFFERING', 'ZPSTR_CONNECTING', 'x-sonosapi-stream')
        title = ''
        artist = ''

        try:
            # title listening radio
            stream_content_element = dom.find('.//r:streamContent', NS)
            if stream_content_element is not None:
                stream_content = stream_content_element.text
                if stream_content:
                    if not stream_content.startswith(ignore_title_string):
                        # if radio, in most cases the following format is used: artist - title
                        #if stream_content is not null, radio is assumed

                        if speaker.radio_station:
                            artist, title = title_artist_parser(speaker.radio_station, stream_content)

            radio_show_element = dom.find('.//r:radioShowMd', NS)
            if radio_show_element is not None:
                radio_show = radio_show_element.text
                if radio_show:
                    # the foramt of a radio_show item seems to be this format:
                    # <radioshow><,p123456> --> rstrip ,p....
                    radio_show = radio_show.split(',p', 1)

                    if len(radio_show) > 1:
                        radio_show = radio_show[0]
                else:
                    radio_show = ''
                speaker.radio_show = radio_show

            album_art = dom.findtext('.//{urn:schemas-upnp-org:metadata-1-0/upnp/}albumArtURI')
            if album_art:
                if not album_art.startswith(('http:', 'https:')):
                    album_art = 'http://' + speaker.ip + ':1400' + album_art
                speaker.track_album_art = album_art

            # mp3, etc -> overrides stream content
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
            speaker.track_artist = artist
            speaker.track_title = title

        except Exception as err:
            print(err)