from __future__ import unicode_literals

# -*- coding: utf-8 -*-
import json
import os
import queue
import socketserver
import weakref
from collections import namedtuple
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import sys
from lib_sonos import definitions
from lib_sonos import sonos_speaker
from lib_sonos.sonos_speaker import SonosSpeaker
from lib_sonos.definitions import SCAN_TIMEOUT
from lib_sonos.radio_parser import title_artist_parser
import socket
import logging
from time import sleep
from soco import discover
from threading import Lock
from soco.data_structures import DidlAudioBroadcast, DidlMusicTrack
from soco.services import zone_group_state_shared_cache
from lib_sonos import utils

try:
    import xml.etree.cElementTree as XML
except ImportError:
    import xml.etree.ElementTree as XML

logger = logging.getLogger('sonos_broker')

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
event_lock = Lock()


class WebserviceHttpHandler(BaseHTTPRequestHandler):
    webroot = None

    def do_GET(self):

        file_handler = None

        try:
            if WebserviceHttpHandler.webroot is None:
                self.send_error(404, 'Service Not Enabled')
                return

            # prevent path traversal
            file_path = os.path.normpath('/' + self.path).lstrip('/')
            file_path = os.path.join(WebserviceHttpHandler.webroot, file_path)

            if not os.path.exists(file_path):
                self.send_error(404, 'File Not Found: %s' % self.path)
                return

            # get registered mime-type
            mime_type = utils.get_mime_type_by_filetype(file_path)

            if mime_type is None:
                self.send_error(406, 'File With Unsupported Media-Type : %s' % self.path)
                return

            client = "{ip}:{port}".format(ip=self.client_address[0], port=self.client_address[1])
            logger.debug("Webservice: delivering file '{path}' to client ip {client}.".format(path=file_path,
                                                                                              client=client))
            file = open(file_path, 'rb').read()
            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Length', sys.getsizeof(file))
            self.end_headers()
            self.wfile.write(file)
        except Exception as ex:
            logger.error("Error delivering file {file}".format(file=file_path))
            logger.error(ex)
        finally:
            self.connection.close()

    def do_POST(self):
        try:
            size = int(self.headers["Content-length"])
            command = self.rfile.read(size).decode('utf-8')

            try:
                from lib_sonos.sonos_commands import MyDecoder
                cmd_obj = json.loads(command, cls=MyDecoder)
            except AttributeError as err:
                err_command = list(filter(None, err.args[0].split("'")))[-1]
                self.make_response(False, "No command '{command}' found!".format(command=err_command))
                return
            status, response = cmd_obj.run()
            self.make_response(status, response)
            logger.debug('Server response -- status: {status} -- response: {response}'.format(status=status,
                                                                                              response=response))
        finally:
            self.connection.close()

    def make_response(self, status, response):
        if status:
            self.send_response(definitions.HTTP_SUCCESS, 'OK')
        else:
            self.send_response(definitions.HTTP_ERROR, 'Bad request')
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("<html><head><title>Sonos Broker</title></head>".encode('utf-8'))
        self.wfile.write("<body>{response}".format(response=response).encode('utf-8'))
        self.wfile.write("</body></html>".encode('utf-8'))


class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    allow_reuse_address = True

    def shutdown(self):
        self.socket.close()
        HTTPServer.shutdown(self)


class SimpleHttpServer:
    def __init__(self, ip, port, root_path):
        self.server = ThreadedHTTPServer((ip, port), WebserviceHttpHandler)
        WebserviceHttpHandler.webroot = root_path

    def start(self):
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    def waitForThread(self):
        self.thread.join()

    def stop(self):
        self.server.shutdown()
        self.waitForThread()


class GetSonosSpeakerThread:
    def __init__(self):
        self._running_flag = False
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.get_speakers_periodically)
        self.thread.daemon = True
        self.thread.start()

    def get_speakers_periodically(self):
        try:
            while not self.stop.wait(1):
                self._running_flag = True
                logger.debug('active threads: {}'.format(len(threading.enumerate())))
                logger.info('scan devices ...')
                zone_group_state_shared_cache.clear()
                SonosServerService.discover()
                logger.debug('Start wait')
                self.stop.wait(SCAN_TIMEOUT)
                logger.debug('Done waiting')
        except Exception as err:
            logger.exception(err)
        finally:
            self._running_flag = False

    def terminate(self):
        self.stop.set()
        logger.debug("GetSonosSpeakerThread terminated")


class SonosEventThread:
    def __init__(self):
        self._running_flag = False
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.process_events)
        self.thread.daemon = True
        self.thread.start()

    def process_events(self):
        speakers = []
        while not self.stop.wait(1):
            try:
                event = SonosSpeaker.event_queue.get()
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

                try:
                    speaker = weakref.proxy(sonos_speaker.sonos_speakers[uid])
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

                SonosSpeaker.event_queue.task_done()

            except queue.Empty:
                pass
            finally:
                if not SonosSpeaker.event_queue.unfinished_tasks:
                    for speaker in speakers:
                        speaker.send()
                    del speakers[:]

        self._running_flag = False

    def handle_AVTransport_event(self, speaker, variables):

        # stop tts from restarting the track
        if 'restart_pending' in variables:
            if variables['restart_pending'] == "1":
                speaker.stop_tts.set()

        if 'current_transport_actions' in variables:
            speaker.transport_actions = variables['current_transport_actions']

        # stop tts thread if an transport error occurred
        if "transport_error_description" in variables:
            speaker.stop_tts.set()

        # meta data for both types (radio, music)
        if 'current_track_uri' in variables:
            speaker.track_uri = variables['current_track_uri']

        if 'current_track' in variables:
            speaker.playlist_position = variables['current_track']

        if 'number_of_tracks' in variables:
            speaker.playlist_total_tracks = variables['number_of_tracks']

        if 'current_playmode' in variables:
            speaker.playmode = variables['current_playmode'].lower()

        if 'transport_state' in variables:
            transport_state = variables['transport_state']
            if transport_state:
                if transport_state.lower() == "transitioning":
                    # because where is no event for current track position, we call it active
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

                    # get current track info, if new track is played or resumed to get track_uri, track_album_art
                    speaker.get_trackposition(force_refresh=True)

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
                    sleep(1)
                    speaker.set_volume(speaker.max_volume, trigger_action=True)
                else:
                    speaker.volume = int(volume)

            volume_lf = variables['volume']['LF']
            if volume_lf:
                if int(volume_lf) < 100:
                    speaker.balance = 100 - int(volume_lf)

            volume_rf = variables['volume']['RF']
            if volume_rf:
                if int(volume_rf) < 100:
                    speaker.balance = int(volume_rf) - 100

        if 'mute' in variables:
            speaker.mute = int(variables['mute']['Master'])

        if 'nightmode' in variables:
            speaker.nightmode = int(variables['nightmode'])

        if 'bass' in variables:
            speaker.bass = int(variables['bass'])

        if 'treble' in variables:
            speaker.treble = int(variables['treble'])

        if 'loudness' in variables:
            speaker.loudness = int(variables['loudness']['Master'])

    def terminate(self):
        self.stop.set()
        logger.debug("SonosEventThread terminated")


# noinspection PyProtectedMember
class SonosServerService(object):

    _sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    _sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    def __init__(self, host, port, server_url, webservice_path, quota, tts_local_mode):
        self.lock = Lock()
        self.host = host
        self.port = port

        self.webservice = SimpleHttpServer(self.host, self.port, webservice_path)
        SonosSpeaker.event_queue = queue.Queue()
        SonosSpeaker.set_tts(webservice_path, server_url, quota, tts_local_mode)

        self.sonos_events_thread = SonosEventThread()
        self.sonos_speakers_thread = GetSonosSpeakerThread()

        'HTTP Server Running...........'
        self.webservice.start()
        self.webservice.waitForThread()

    def terminate_threads(self):
        self.webservice.stop()
        self.sonos_speakers_thread.terminate()
        self.sonos_events_thread.terminate()

    def unsubscribe_speaker_events(self):
        for speaker in sonos_speaker.sonos_speakers.values():
            speaker.event_unsubscribe()

    @staticmethod
    def _discover():
        return discover(timeout=10, include_invisible=False)

    @classmethod
    def discover(cls):
        try:
            with sonos_speaker._sonos_lock:

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
                            speaker_to_remove.append(uid)
                            continue
                        try:
                            _sp = SonosSpeaker(soco_speaker)
                            sonos_speaker.sonos_speakers[uid] = _sp
                        except Exception as ex:
                            speaker_to_remove.append(uid)
                            continue  # speaker maybe deleted by another thread
                    else:
                        try:
                            sonos_speaker.sonos_speakers[uid].soco.get_speaker_info(refresh=True)
                            active_uids.append(uid)
                        except Exception:
                            speaker_to_remove.append(uid)
                            continue  # speaker maybe deleted by another thread
                try:
                    offline_uids = set(list(sonos_speaker.sonos_speakers.keys())) - set(active_uids)
                    offline_uids = set(list(offline_uids) + speaker_to_remove)
                except KeyError as err:
                    print(err)
                    pass  # speaker maybe deleted by another thread

                for uid in offline_uids:
                    logger.info("offline speaker: {uid} -- removing from list (maybe cached)".format(uid=uid))
                    try:
                        sonos_speaker.sonos_speakers[uid].status = False
                        sonos_speaker.sonos_speakers[uid].send()
                        sonos_speaker.sonos_speakers[uid].terminate()
                    except KeyError:
                        continue  # speaker maybe deleted by another thread
                    finally:
                        try:
                            del sonos_speaker.sonos_speakers[uid]
                        except:
                            pass

                # register events for all speaker, this has to be the last step due to some logics in the event
                # handling routine

                logger.debug("DISCOVERED +++++++++++++++++++++++++++++++++++++++++++++++++++")
                for speaker in sonos_speaker.sonos_speakers.values():
                    logger.debug("discovered speaker: {0}".format(speaker.uid))

                    try:
                        speaker.set_zone_coordinator()
                        speaker.set_group_members()
                        speaker.event_subscription()
                    except KeyError:
                        pass  # speaker maybe deleted by another thread

        except ReferenceError:
            pass
        except Exception as err:
            logger.exception('Error in method discover()!\nError: {err}'.format(err=err))
        finally:
            pass

    @staticmethod
    def set_music_data(speaker, variables):

        if 'current_track_duration' in variables:
            speaker.track_duration = variables['current_track_duration']

        music_data = variables['current_track_meta_data']
        if music_data:
            track_album_art = ''
            track_album = ''
            track_title = ''
            track_artist = ''

            if hasattr(music_data, 'album_art_uri'):
                if music_data.album_art_uri:
                    if not music_data.album_art_uri.startswith(('http:', 'https:')):
                        track_album_art = 'http://' + speaker.ip + ':1400' + music_data.album_art_uri

            if hasattr(music_data, 'album'):
                track_album = music_data.album

            if hasattr(music_data, 'title'):
                track_title = music_data.title

            if hasattr(music_data, 'creator'):
                track_artist = music_data.creator

            if not isinstance(variables['current_track_meta_data'], DidlMusicTrack):
                # radio stream
                speaker.streamtype = "radio"
                speaker.track_duration = "00:00:00"
                speaker.radio_station = ''
                speaker.radio_show = ''

                radio_station_title = variables['enqueued_transport_uri_meta_data']

                if hasattr(radio_station_title, 'title'):
                    speaker.radio_station = radio_station_title.title

                if hasattr(music_data, 'radio_show'):
                    # the format of a radio_show item seems to be this format:
                    # <radioshow><,p123456> --> rstrip ,p....
                    radio_show = music_data.radio_show
                    if radio_show:
                        radio_show = radio_show.split(',p', 1)
                        if len(radio_show) > 1:
                            speaker.radio_show = radio_show[0]

                if hasattr(music_data, 'stream_content'):
                    ignore_title_string = ('ZPSTR_BUFFERING', 'ZPSTR_BUFFERING', 'ZPSTR_CONNECTING', 'x-sonosapi-stream')
                    track_artist = ''
                    track_title = ''

                    stream_content = music_data.stream_content

                    if stream_content:
                        if not stream_content.startswith(ignore_title_string):
                            # if radio, in most cases the following format is used: artist - title
                            # if stream_content is not null, radio is assumed

                            track_artist, track_title = title_artist_parser(speaker.radio_station if speaker.radio_station
                                                                            else '', stream_content)
            else:
                speaker.streamtype = "music"
                speaker.radio_show = ''
                speaker.radio_station = ''

            speaker.track_artist = track_artist
            speaker.track_title = track_title
            speaker.track_album_art = track_album_art
            speaker.track_album = track_album

