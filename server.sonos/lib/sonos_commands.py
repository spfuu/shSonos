# -*- coding: utf-8 -*-

import argparse
import re
from urllib.parse import unquote_plus
from lib import sonos_speaker
from lib.udp_broker import UdpResponse, UdpBroker
from lib.sonos_service import SonosServerService

class Command():
    def __init__(self, service):
        self.sonos_service = service
        self.true_vars = ['true', '1', 't', 'y', 'yes']

    def do_work(self, client_ip, path):

        response = 'Unknown command'
        try:
            command = path.lower()
            command = re.sub("^/|/$", '', command).split('/')

            if command[0].lower() == 'speaker':
                " input is : speaker/uid/property/action/value" \
                " we're changing uid with property to get better handling with slices"

                c1 = command[1]
                c2 = command[2]

                command[1] = c2
                command[2] = c1

            if command:
                do_work = getattr(self, "{}_{}".format(command[0], command[1]))
                return do_work(client_ip, command[2:])
        except:
            return False, response

    def client_subscribe(self, ip, arguments):
        try:
            port = int(arguments[0])
            UdpBroker.subscribe_client(ip, port)
            return True, 'Successfully subscribed client {}:{}'.format(ip, port)
        except:
            return False, "Couldn't subscribe client {}:{}".format(ip, port)

    def client_unsubscribe(self, ip, arguments):
        try:
            port = int(arguments[0])
            UdpBroker.unsubscribe_client(ip, port)
            return True, 'Successfully unsubscribed client {}:{}'.format(ip, port)
        except:
            return False, "Couldn't unsubscribe client {}:{}".format(ip, port)

    def client_list(self, ip, arguments):
        try:
            speakers = self.get_speakers()

            data = ''

            for uid, speaker in speakers.items():
                data += "<p>uid   : {}</p>".format(speaker.uid)
                data += "<p>ip    : {}</p>".format(speaker.ip)
                data += "<p>model : {}</p>".format(speaker.model)
                data += "<p>-------------------------------------------</p><p></p><p></p>"

            if not data:
                data = "no speakers online!"

            return True, data
        except:
            return False, "Couldn't list speakers"

    def speaker_stop(self, ip, arguments):
        try:
            uid = arguments[0].lower()
            soco = SonosServerService.get_soco(uid)

            action = ''

            if len(arguments) > 2:
                action = arguments[1]

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            if action == 'set':
                try:
                    value = arguments[2]
                    if value in self.true_vars:
                        soco.stop()
                        sonos_speaker.sonos_speakers[uid].stop = 1
                        sonos_speaker.sonos_speakers[uid].play = 0
                        sonos_speaker.sonos_speakers[uid].pause = 0
                    else:
                        soco.play()
                        sonos_speaker.sonos_speakers[uid].stop = 0
                        sonos_speaker.sonos_speakers[uid].play = 1
                        sonos_speaker.sonos_speakers[uid].pause = 0

                except:
                    raise Exception("Couldn't set stop status for speaker with uid '{}'!".format(uid))

            try:
                data = "%s\r\n" % UdpResponse.stop(uid)
                data += "%s\r\n" % UdpResponse.play(uid)
                data += "%s\r\n" % UdpResponse.pause(uid)
                UdpBroker.udp_send(data)

                return True, "Successfully send stop status for speaker with uid '{}'.".format(uid)
            except:
                raise Exception("Couldn't get stop status for speaker with uid '{}'!".format(uid))

        except Exception as err:
            return False, err

    def speaker_play(self, ip, arguments):
        try:
            uid = arguments[0].lower()
            soco = SonosServerService.get_soco(uid)

            action = ''

            if len(arguments) > 2:
                action = arguments[1]

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            if action == 'set':
                try:
                    value = arguments[2]
                    if value in self.true_vars:
                        soco.play()
                        sonos_speaker.sonos_speakers[uid].stop = 0
                        sonos_speaker.sonos_speakers[uid].play = 1
                        sonos_speaker.sonos_speakers[uid].pause = 0
                    else:
                        soco.stop()
                        sonos_speaker.sonos_speakers[uid].stop = 1
                        sonos_speaker.sonos_speakers[uid].play = 0
                        sonos_speaker.sonos_speakers[uid].pause = 0
                except:
                    raise Exception("Couldn't set play status for speaker with uid '{}'!".format(uid))
            try:
                data = "%s\n" % UdpResponse.stop(uid)
                data += "%s\n" % UdpResponse.play(uid)
                data += "%s\n" % UdpResponse.pause(uid)
                UdpBroker.udp_send(data)

                return True, "Successfully send play status for speaker with uid '{}'.".format(uid)
            except:
                raise Exception("Couldn't get play status for speaker with uid '{}'!".format(uid))


        except Exception as err:
            return False, err

    def speaker_pause(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            action = ''

            if len(arguments) > 2:
                action = arguments[1]

            soco = SonosServerService.get_soco(uid)

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            if action == 'set':
                try:
                    value = arguments[2]
                    if value in self.true_vars:
                        soco.pause()
                        sonos_speaker.sonos_speakers[uid].stop = 0
                        sonos_speaker.sonos_speakers[uid].play = 0
                        sonos_speaker.sonos_speakers[uid].pause = 1
                    else:
                        soco.play()
                        sonos_speaker.sonos_speaker.sonos_speakers[uid].stop = 0
                        sonos_speaker.sonos_speakers[uid].play = 1
                        sonos_speaker.sonos_speakers[uid].pause = 0

                except:
                    raise Exception("Couldn't set pause status for speaker with uid '{}'!".format(uid))

            try:
                data = "%s\r\n" % UdpResponse.stop(uid)
                data += "%s\r\n" % UdpResponse.play(uid)
                data += "%s\r\n" % UdpResponse.pause(uid)
                UdpBroker.udp_send(data)

                return True, "Successfully send pause status for speaker with uid '{}'.".format(uid)
            except:
                raise Exception("Couldn't get pause status for speaker with uid '{}'!".format(uid))


        except Exception as err:
            return False, err

    def speaker_mute(self, ip, arguments):
        try:
            uid = arguments[0].lower()
            action = ''

            if len(arguments) > 2:
                action = arguments[1]

            soco = SonosServerService.get_soco(uid)

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            if action == 'set':
                try:
                    value = arguments[2]
                    if value in self.true_vars:
                        soco.mute = True
                        sonos_speaker.sonos_speakers[uid].mute = 1
                    else:
                        soco.mute = False
                        sonos_speaker.sonos_speakers[uid].mute = 0
                except:
                    raise Exception("Couldn't set mute status for speaker with uid '{}'!".format(uid))
            try:
                data = UdpResponse.mute(uid)
                UdpBroker.udp_send(data)

                return True, "Successfully send mute status for speaker with uid '{}'.".format(uid)
            except:
                raise Exception("Couldn't get mute status for speaker with uid '{}'!".format(uid))

        except Exception as err:
            return False, err

    def speaker_led(self, ip, arguments):
        try:
            uid = arguments[0].lower()
            action = ''

            #pydevd.settrace('192.168.178.44', port=12000, stdoutToServer=True, stderrToServer=True)

            if len(arguments) > 2:
                action = arguments[1]

            soco = SonosServerService.get_soco(uid)

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            if action == 'set':
                try:
                    value = arguments[2]
                    if value in self.true_vars:
                        soco.status_light = True
                        sonos_speaker.sonos_speakers[uid].led = 1
                    else:
                        soco.status_light = False
                        sonos_speaker.sonos_speakers[uid].led = 0
                except:
                    raise Exception("Couldn't set led status for speaker with uid '{}'!".format(uid))
            try:

                data = UdpResponse.led(uid)
                UdpBroker.udp_send(data)

                return True, "Successfully send led status for speaker with uid '{}'.".format(uid)
            except Exception:
                raise Exception("Couldn't get led status for speaker with uid '{}'!".format(uid))

        except Exception as err:
            return False, err

    def speaker_volume(self, ip, arguments):
        try:
            uid = arguments[0].lower()
            action = ''

            if len(arguments) > 2:
                action = arguments[1]

            soco = SonosServerService.get_soco(uid)

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            if action == 'set':
                try:
                    value = arguments[2]
                    check_volume_range(value)
                    soco.volume = value
                    sonos_speaker.sonos_speakers[uid].volume = value
                except:
                    raise Exception("Couldn't set volume for speaker with uid '{}'!".format(uid))
            try:
                data = UdpResponse.volume(uid)
                UdpBroker.udp_send(data)

                return True, "Successfully send volume status for speaker with uid '{}'.".format(uid)
            except Exception:
                raise Exception("Couldn't get volume for speaker with uid '{}'!".format(uid))

        except Exception as err:
            return False, err


    def speaker_seek(self, ip, arguments):
        try:
            uid = arguments[0].lower()
            action = ''

            if len(arguments) > 2:
                action = arguments[1]

            soco = SonosServerService.get_soco(uid)

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            if action == 'set':
                try:
                    timestamp = arguments[2]
                    print(timestamp)
                    soco.seek(timestamp)
                except:
                    raise Exception("Couldn't seek speaker with uid '{}'!".format(uid))

            return True, "Successfully send seek command for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, err

    def speaker_track_duration(self, ip, arguments):
        try:
            uid = arguments[0].lower()
            soco = SonosServerService.get_soco(uid)

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            try:
                track_duration = soco.get_current_track_info()['duration']

                if not track_duration:
                    track_duration = "00:00:00"
                sonos_speaker.sonos_speakers[uid].track_duration = track_duration

            except:
                raise Exception("Couldn't get current track duration for speaker with uid '{}'!".format(uid))
            try:
                data = UdpResponse.track_duration(uid)
                UdpBroker.udp_send(data)
                return True, "Successfully send current track duration for speaker with uid '{}'.".format(uid)

            except Exception:
                raise Exception("Couldn't get current track duration for speaker with uid '{}'!".format(uid))

        except Exception as err:
            return False, err

    def speaker_track_position(self, ip, arguments):
        try:
            uid = arguments[0].lower()
            soco = SonosServerService.get_soco(uid)

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            try:
                track_position = soco.get_current_track_info()['position']

                if not track_position:
                    track_position = "00:00:00"

                sonos_speaker.sonos_speakers[uid].track_position = track_position

            except:
                raise Exception("Couldn't get track position for speaker with uid '{}'!".format(uid))
            try:
                data = UdpResponse.track_position(uid)
                UdpBroker.udp_send(data)
                return True, "Successfully send current track position for speaker with uid '{}'.".format(uid)

            except Exception:
                raise Exception("Couldn't get current track position for speaker with uid '{}'!".format(uid))

        except Exception as err:
            return False, err


    def speaker_track(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            soco = SonosServerService.get_soco(uid)

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            try:
                #" 'title' 'artist' 'album' 'album_art'  'position' 'playlist_position' 'duration' 'TrackDuration' 'uri' 'position'"
                track = soco.get_current_track_info()['title']
                sonos_speaker.sonos_speakers[uid].track = track

            except:
                raise Exception("Couldn't get current track title for speaker with uid '{}'!".format(uid))
            try:
                data = UdpResponse.track(uid)
                UdpBroker.udp_send(data)
                return True, "Successfully send current track title for speaker with uid '{}'.".format(uid)

            except Exception:
                raise Exception("Couldn't get current track title for speaker with uid '{}'!".format(uid))

        except Exception as err:
            return False, err

    def speaker_artist(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            soco = SonosServerService.get_soco(uid)

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            try:
                #" 'title' 'artist' 'album' 'album_art'  'position' 'playlist_position' 'duration' 'TrackDuration' 'uri' 'position'"
                artist = soco.get_current_track_info()['artist']
                sonos_speaker.sonos_speakers[uid].artist = artist

            except:
                raise Exception("Couldn't get current track artist for speaker with uid '{}'!".format(uid))
            try:
                data = UdpResponse.artist(uid)
                UdpBroker.udp_send(data)
                return True, "Successfully send current track artist for speaker with uid '{}'.".format(uid)

            except Exception:
                raise Exception("Couldn't get current track artist for speaker with uid '{}'!".format(uid))

        except Exception as err:
            return False, err

    def speaker_play_uri(self, ip, arguments):
        try:
            uid = arguments[0].lower()
            action = ''

            if len(arguments) > 2:
                action = arguments[1]

            soco = SonosServerService.get_soco(uid)

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            if action == 'set':
                try:
                    play_uri = unquote_plus(arguments[2])
                    print(play_uri)
                    soco.play_uri(play_uri)
                except:
                    raise Exception("Couldn't set uri for speaker with uid '{}'!".format(uid))

        except Exception as err:
            return False, err


    def speaker_streamtype(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            soco = SonosServerService.get_soco(uid)

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            #no soco implementation, use our speaker info (gathered by sonos events)
            try:
                data = UdpResponse.streamtype(uid)
                UdpBroker.udp_send(data)
                return True, "Successfully send streamtype for speaker with uid '{}'.".format(uid)

            except Exception:
                raise Exception("Couldn't get streamtype for speaker with uid '{}'!".format(uid))

        except Exception as err:
            return False, err



def check_volume_range(volume):
    value = int(volume)

    if value < 0 or value > 100:
        msg = 'Volume has to be between 0 and 100.'
        raise argparse.ArgumentTypeError(msg)

    return value
