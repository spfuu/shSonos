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
from soco.data_structures import DidlAudioBroadcast
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

    @staticmethod
    def _discover():
        return discover(timeout=5, include_invisible=False)

    def discover(self):
        try:
            with sonos_speaker._sonos_lock:
                zone_group_state_shared_cache.clear()
                active_uids = []
                soco_speakers = SonosServerService._discover()

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
                            sonos_speaker.sonos_speakers[uid].model = SonosServerService.get_model_name(
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

                # remove all offline speakers from internal list
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

                # register events for all speaker, this has to be the last step due to some logics in the event
                # handling routine

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
                if event is None:
                    return

                uid = event.sid.lower().rsplit('_sub', 1)

                if not uid:
                    print("No a valid event subscription id: {}".format(event.sid.lower()))
                    return

                uid = uid[0]
                uid = uid.rsplit('uuid:', 1)

                if not uid:
                    print("No a valid event subscription id: {}".format(event.sid.lower()))
                    return

                uid = uid[1]

                if uid not in sonos_speaker.sonos_speakers:
                    print("No sonos speaker found for subscription {}".format(event.sid.lower()))
                    continue

                with sonos_speaker._sonos_lock:
                    try:
                        speaker = sonos_speaker.sonos_speakers[uid]
                        if speaker not in speakers:
                            speakers.append(speaker)
                    except KeyError:
                        pass  # speaker maybe removed from another thread

                if event.service.service_type == 'ZoneGroupTopology':
                    speaker.set_zone_coordinator()
                    speaker.set_group_members()
                    speaker.dirty_music_metadata()

                if event.service.service_type == 'AVTransport':
                    self.handle_AVTransport_event(speaker, event.variables)

                if event.service.service_type == 'RenderingControl':
                    self.handle_RenderingControl_event(speaker, event.variables)

                if event.service.service_type == 'AlarmClock':
                    self.handle_AlarmClock_event(speaker, event.variables)

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
    @staticmethod
    def get_model_name(ip):
        response = requests.get('http://' + ip + ':1400/xml/device_description.xml')
        dom = XML.fromstring(response.content)

        if dom.findtext('.//{urn:schemas-upnp-org:device-1-0}modelName') is not None:
            return dom.findtext('.//{urn:schemas-upnp-org:device-1-0}modelName')

        return ""

    @staticmethod
    def set_radio_data(speaker, variables):

        speaker.streamtype = "radio"
        speaker.track_duration = "00:00:00"
        speaker.radio_station = ''
        speaker.radio_show = ''

        radio_station_title = variables['enqueued_transport_uri_meta_data']
        radio_data = variables['current_track_meta_data']

        if hasattr(radio_station_title, 'title'):
            speaker.radio_station = radio_station_title.title

        if hasattr(radio_data, 'radio_show'):
            # the format of a radio_show item seems to be this format:
            # <radioshow><,p123456> --> rstrip ,p....
            radio_show = radio_data.radio_show
            if radio_show:
                radio_show = radio_show.split(',p', 1)
                if len(radio_show) > 1:
                    speaker.radio_show = radio_show[0]

        if hasattr(radio_data, 'album_art_uri'):
            speaker.track_album_art = ''
            album_art = radio_data.album_art_uri
            if album_art:
                if not album_art.startswith(('http:', 'https:')):
                    album_art = 'http://' + speaker.ip + ':1400' + album_art
                speaker.track_album_art = album_art

        if hasattr(radio_data, 'stream_content'):
            ignore_title_string = ('ZPSTR_BUFFERING', 'ZPSTR_BUFFERING', 'ZPSTR_CONNECTING', 'x-sonosapi-stream')
            artist = ''
            title = ''

            stream_content = radio_data.stream_content

            if stream_content:
                if not stream_content.startswith(ignore_title_string):
                    # if radio, in most cases the following format is used: artist - title
                    #if stream_content is not null, radio is assumed

                    artist, title = title_artist_parser(speaker.radio_station if speaker.radio_station else '',
                                                        stream_content)
            speaker.track_artist = artist
            speaker.track_title = title

    @staticmethod
    def set_music_data(speaker, variables):
        speaker.streamtype = "music"
        speaker.radio_show = ''
        speaker.radio_station = ''

        if 'current_track_duration' in variables:
            speaker.track_duration = variables['current_track_duration']

        ml_track = variables['current_track_meta_data']
        if ml_track:
            if hasattr(ml_track, 'album_art_uri'):
                if not ml_track.album_art_uri.startswith(('http:', 'https:')):
                    album_art_uri = 'http://' + speaker.ip + ':1400' + ml_track.album_art_uri
                speaker.track_album_art = album_art_uri
            else:
                speaker.track_album_art = ''

            if hasattr(ml_track, 'album'):
                speaker.track_album = ml_track.album
            else:
                speaker.track_album = ''

            if hasattr(ml_track, 'title'):
                speaker.track_title = ml_track.title
            else:
                speaker.title = ''

            if hasattr(ml_track, 'creator'):
                speaker.track_artist = ml_track.creator
            else:
                speaker.track_artist = ''

    def handle_AVTransport_event(self, speaker, variables):

        # meta data for both types (radio, music)
        if 'current_track_uri' in variables:
            speaker.track_uri = variables['current_track_uri']

        if 'current_playmode' in variables:
            speaker.playmode = variables['current_playmode'].lower()

        if 'transport_state' in variables:
            transport_state = variables['transport_state']
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

        if 'enqueued_transport_uri_meta_data' in variables:
            if isinstance(variables['enqueued_transport_uri_meta_data'], DidlAudioBroadcast):
                SonosServerService.set_radio_data(speaker, variables)
            else:
                SonosServerService.set_music_data(speaker, variables)

    def handle_AlarmClock_event(self, speaker, variables):
        """
        There seems no additional info in variables. The event only gives us the event subscription id.
        So we call the get_alarms routine.
        """
        speaker.get_alarms()

    def handle_RenderingControl_event(self, speaker, variables):

        if 'volume' in variables:
            volume = variables['volume']['Master']
            if volume:
                if utils.check_max_volume_exceeded(volume, speaker.max_volume):
                    speaker.set_volume(speaker.max_volume, trigger_action=True)
                else:
                    speaker.volume = int(volume)

        if 'mute' in variables:
            speaker.mute = int(variables['mute']['Master'])

        if 'bass' in variables:
            speaker.bass = int(variables['bass'])

        if 'treble' in variables:
            speaker.treble = int(variables['treble'])

        if 'loudness' in variables:
            speaker.loudness = int(variables['loudness']['Master'])