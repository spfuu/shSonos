import argparse
import re
import udp_broker
import sonos_service

#import sys
#sys.path.append('/usr/smarthome/plugins/sonos/server/pycharm-debug-py3k.egg')
#import pydevd


class Command():
    def __init__(self, service):
        self.sonos_service = service
        self.true_vars = ['true', '1', 't', 'y', 'yes']

    def do_work(self, client_ip, path):

        response = 'Unknown command'
        try:
            print(client_ip)
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
            udp_broker.UdpBroker.subscribe_client(ip, port)
            return True, 'Successfully subscribed client {}:{}'.format(ip, port)
        except:
            return False, "Couldn't subscribe client {}:{}".format(ip, port)

    def client_unsubscribe(self, ip, arguments):
        try:
            port = int(arguments[0])
            udp_broker.UdpBroker.unsubscribe_client(ip, port)
            return True, 'Successfully unsubscribed client {}:{}'.format(ip, port)
        except:
            return False, "Couldn't unsubscribe client {}:{}".format(ip, port)

    def client_list(self, ip, arguments):
        try:
            speakers = self.sonos_service.get_speakers()

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
            soco = self.sonos_service.get_soco(uid)

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
                        sonos_service.sonos_speakers[uid].stop = 1
                        sonos_service.sonos_speakers[uid].play = 0
                        sonos_service.sonos_speakers[uid].pause = 0
                    else:
                        soco.play()
                        sonos_service.sonos_speakers[uid].stop = 0
                        sonos_service.sonos_speakers[uid].play = 1
                        sonos_service.sonos_speakers[uid].pause = 0

                except:
                    raise Exception("Couldn't set stop status for speaker with uid '{}'!".format(uid))

            try:
                data = "%s\r\n" % udp_broker.UdpResponse.stop(uid)
                data += "%s\r\n" % udp_broker.UdpResponse.play(uid)
                data += "%s\r\n" % udp_broker.UdpResponse.pause(uid)
                udp_broker.UdpBroker.udp_send(data)

                return True, "Successfully send stop status for speaker with uid '{}'.".format(uid)
            except:
                raise Exception("Couldn't get stop status for speaker with uid '{}'!".format(uid))

        except Exception as err:
            return False, err

    def speaker_play(self, ip, arguments):
        try:
            uid = arguments[0].lower()
            soco = self.sonos_service.get_soco(uid)

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
                        sonos_service.sonos_speakers[uid].stop = 0
                        sonos_service.sonos_speakers[uid].play = 1
                        sonos_service.sonos_speakers[uid].pause = 0
                    else:
                        soco.stop()
                        sonos_service.sonos_speakers[uid].stop = 1
                        sonos_service.sonos_speakers[uid].play = 0
                        sonos_service.sonos_speakers[uid].pause = 0
                except:
                    raise Exception("Couldn't set play status for speaker with uid '{}'!".format(uid))
            try:
                data = "%s\n" % udp_broker.UdpResponse.stop(uid)
                data += "%s\n" % udp_broker.UdpResponse.play(uid)
                data += "%s\n" % udp_broker.UdpResponse.pause(uid)
                udp_broker.UdpBroker.udp_send(data)

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

            soco = self.sonos_service.get_soco(uid)

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            if action == 'set':
                try:
                    value = arguments[2]
                    if value in self.true_vars:
                        soco.pause()
                        sonos_service.sonos_speakers[uid].stop = 0
                        sonos_service.sonos_speakers[uid].play = 0
                        sonos_service.sonos_speakers[uid].pause = 1
                    else:
                        soco.play()
                        sonos_service.sonos_speakers[uid].stop = 0
                        sonos_service.sonos_speakers[uid].play = 1
                        sonos_service.sonos_speakers[uid].pause = 0

                except:
                    raise Exception("Couldn't set pause status for speaker with uid '{}'!".format(uid))

            try:
                data = "%s\r\n" % udp_broker.UdpResponse.stop(uid)
                data += "%s\r\n" % udp_broker.UdpResponse.play(uid)
                data += "%s\r\n" % udp_broker.UdpResponse.pause(uid)
                udp_broker.UdpBroker.udp_send(data)

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

            soco = self.sonos_service.get_soco(uid)

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            if action == 'set':
                try:
                    value = arguments[2]
                    if value in self.true_vars:
                        soco.mute = True
                        sonos_service.sonos_speakers[uid].mute = 1
                    else:
                        soco.mute = False
                        sonos_service.sonos_speakers[uid].mute = 0
                except:
                    raise Exception("Couldn't set mute status for speaker with uid '{}'!".format(uid))
            try:
                data = udp_broker.UdpResponse.mute(uid)
                udp_broker.UdpBroker.udp_send(data)

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

            soco = self.sonos_service.get_soco(uid)

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            if action == 'set':
                try:
                    value = arguments[2]
                    if value in self.true_vars:
                        soco.status_light = True
                        sonos_service.sonos_speakers[uid].led = 1
                    else:
                        soco.status_light = False
                        sonos_service.sonos_speakers[uid].led = 0
                except:
                    raise Exception("Couldn't set led status for speaker with uid '{}'!".format(uid))
            try:

                data = udp_broker.UdpResponse.led(uid)
                udp_broker.UdpBroker.udp_send(data)

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

            soco = self.sonos_service.get_soco(uid)

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            if action == 'set':
                try:
                    value = arguments[2]
                    check_volume_range(value)
                    soco.volume = value
                    sonos_service.sonos_speakers[uid].volume = value
                except:
                    raise Exception("Couldn't set volume for speaker with uid '{}'!".format(uid))
            try:
                data = udp_broker.UdpResponse.volume(uid)
                udp_broker.UdpBroker.udp_send(data)

                return True, "Successfully send volume status for speaker with uid '{}'.".format(uid)
            except Exception:
                raise Exception("Couldn't get volume for speaker with uid '{}'!".format(uid))

        except Exception as err:
            return False, err

    def speaker_track(self, ip, arguments):
        try:
            uid = arguments[0].lower()
            action = ''

            if len(arguments) > 2:
                action = arguments[1]

            soco = self.sonos_service.get_soco(uid)

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            try:
                #" 'title' 'artist' 'album' 'album_art'  'position' 'playlist_position' 'duration' 'TrackDuration' 'uri' 'position'"
                track = soco.get_current_track_info()['title']
                sonos_service.sonos_speakers[uid].track = track

            except:
                raise Exception("Couldn't get current track title for speaker with uid '{}'!".format(uid))
            try:
                data = udp_broker.UdpResponse.track(uid)
                udp_broker.UdpBroker.udp_send(data)
                return True, "Successfully send current track title for speaker with uid '{}'.".format(uid)

            except Exception:
                raise Exception("Couldn't get current track title for speaker with uid '{}'!".format(uid))

        except Exception as err:
            return False, err

    def speaker_artist(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if len(arguments) > 2:
                action = arguments[1]

            soco = self.sonos_service.get_soco(uid)

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            try:
                #" 'title' 'artist' 'album' 'album_art'  'position' 'playlist_position' 'duration' 'TrackDuration' 'uri' 'position'"
                artist = soco.get_current_track_info()['artist']
                sonos_service.sonos_speakers[uid].artist = artist

            except:
                raise Exception("Couldn't get current track artist for speaker with uid '{}'!".format(uid))
            try:
                data = udp_broker.UdpResponse.artist(uid)
                udp_broker.UdpBroker.udp_send(data)
                return True, "Successfully send current track artist for speaker with uid '{}'.".format(uid)

            except Exception:
                raise Exception("Couldn't get current track artist for speaker with uid '{}'!".format(uid))

        except Exception as err:
            return False, err

    def speaker_streamtype(self, ip, arguments):
        try:
            uid = arguments[0].lower()
            action = ''

            if len(arguments) > 2:
                action = arguments[1]

            soco = self.sonos_service.get_soco(uid)

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            #no soco implementation, use our speaker info (gathered by sonos events)
            try:
                data = udp_broker.UdpResponse.streamtype(uid)
                udp_broker.UdpBroker.udp_send(data)
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
