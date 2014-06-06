# -*- coding: utf-8 -*-
import re
from urllib.parse import unquote_plus
from lib_sonos import sonos_speaker
from lib_sonos.sonos_library import SonosLibrary
from lib_sonos.udp_broker import UdpBroker
from lib_sonos.definitions import SCAN_TIMEOUT
from lib_sonos import utils

class Command():
    def __init__(self, service):
        self.sonos_service = service
        self.sonos_library = SonosLibrary()
        self.true_vars = ['true', '1', 't', 'y', 'yes']

    def do_work(self, client_ip, path):

        response = 'Unknown command'
        try:
            command = path
            command = re.sub("^/|/$", '', command).split('/')

            if command[0].lower() == 'speaker':
                " input is : speaker/uid/property/action/value" \
                " we're changing uid with property to get better handling with slices"
                c1 = command[1]
                c2 = command[2]
                command[1] = c2
                command[2] = c1

            if len(command) > 1:
                do_work = getattr(self, "{}_{}".format(command[0], command[1]))
                return do_work(client_ip, command[2:])
            else:
                do_work = getattr(self, command[0])
                return do_work(client_ip, None)

        except Exception as err:
            print(err)
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
            data = ''
            for uid, speaker in sonos_speaker.sonos_speakers.items():
                data += "<p>uid             : {}</p>".format(speaker.uid)
                data += "<p>ip              : {}</p>".format(speaker.ip)
                data += "<p>model           : {}</p>".format(speaker.model)
                data += "<p>current zone    : {}</p>".format(speaker.zone_name)
                data += "<p>-------------------------------------------</p><p></p><p></p>"

            if not data:
                data = "No speakers online! Discover scan is performed every {} seconds.".format(SCAN_TIMEOUT)

            return True, data
        except:
            return False, "Couldn't list speakers"

    def speaker_current_state(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].send_data(force=True)

            return True, "CURRENTSTATE command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("CURRENTSTATE command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_trackinfo(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].track_info()
            sonos_speaker.sonos_speakers[uid].send_data()

            return True, "TRACKINFO command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("TRACKINFO command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_play_uri(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:
                uri = unquote_plus(arguments[1])
                uri = utils.url_fix(uri)
                sonos_speaker.sonos_speakers[uid].play_uri(uri.decode())
            else:
                raise Exception("Missing arguments")

            #we need no explicit response here, play uri event triggers the update
            return True, "PLAYURI command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("PLAYURI command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_play_snippet(self, ip, arguments):
        try:
            volume = -1
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:
                uri = unquote_plus(arguments[1])
                uri = utils.url_fix(uri)
            else:
                raise Exception("Missing arguments!")

            if len(arguments) > 2:
                volume = int(arguments[2])
                if volume < -1 or volume > 100:
                    volume = -1

            sonos_speaker.sonos_speakers[uid].play_snippet(uri.decode(), volume)

            #we need no explicit response here, playsnippet event triggers the update

            return True, "PLAYSNIPPET command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("PLAYSNIPPET command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_play_tts(self, ip, arguments):
        try:

            if not self.sonos_service.tts_enabled:
                return False, 'Google-TTS not active. Check server logs!'

            volume = -1

            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:
                tts = arguments[1]
                tts = unquote_plus(tts)
                tts = (tts[:100]) if len(tts) > 100 else tts
            else:
                raise Exception("Missing arguments!")

            if len(arguments) > 2:
                language = arguments[2]
                if not language:
                    language = 'en'
            else:
                language = 'en'

            if len(arguments) > 3:
                volume = int(arguments[3])
                if volume < -1 or volume > 100:
                    volume = -1

            sonos_speaker.sonos_speakers[uid].play_tts(tts, volume, self.sonos_service.smb_url,
                                                       self.sonos_service.local_share, language, self.sonos_service.quota)
            #we need no explicit response here, playtts event triggers the update

            return True, "PLAYTTS command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("PLAYTTS command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_next(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].next()

            #we need no explicit response here, next title event triggers the update

            return True, "NEXT command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("NEXT command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_previous(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].previous()

            #we need no explicit response here, previous title event triggers the update

            return True, "PREVIOUS command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("PREVIOUS command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_seek(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:
                timestamp = arguments[1]
                sonos_speaker.sonos_speakers[uid].seek(timestamp)

            #we need no explicit response here, next title event triggers the update

            return True, "SEEK command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("SEEK command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_stop(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].stop = not sonos_speaker.sonos_speakers[uid].stop
            sonos_speaker.sonos_speakers[uid].send_data()

            return True, "STOP command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("STOP command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_play(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].play = not sonos_speaker.sonos_speakers[uid].play
            sonos_speaker.sonos_speakers[uid].send_data()

            return True, "PLAY command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("PLAY command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_pause(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].pause = not sonos_speaker.sonos_speakers[uid].pause
            sonos_speaker.sonos_speakers[uid].send_data()

            return True, "PAUSE command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("PAUSE command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_mute(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].mute = not sonos_speaker.sonos_speakers[uid].mute
            sonos_speaker.sonos_speakers[uid].send_data()

            return True, "MUTE command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("MUTE command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_led(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].led = not sonos_speaker.sonos_speakers[uid].led
            sonos_speaker.sonos_speakers[uid].send_data()

            return True, "LED command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("LED command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_volume_up(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].volume_up()

            return True, "VOLUME_UP command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("VOLUME_UP command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_volume_down(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].volume_down()

            return True, "VOLUME_DOWN command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("VOLUME_DOWN command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_volume(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:
                value = int(arguments[1])
                sonos_speaker.sonos_speakers[uid].volume = value

            sonos_speaker.sonos_speakers[uid].send_data()

            return True, "VOLUME command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("VOLUME command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_maxvolume(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:
                value = int(arguments[1])
                sonos_speaker.sonos_speakers[uid].max_volume = value

            sonos_speaker.sonos_speakers[uid].send_data()

            return True, "MAXVOLUME command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("MAXVOLUME command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_join(selfself, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:
                uid_to_join = arguments[1].lower()

                if uid_to_join not in sonos_speaker.sonos_speakers:
                    raise Exception("No speaker found with uid '{}' for joining.".format(uid_to_join))

                sonos_speaker.sonos_speakers[uid].join(sonos_speaker.sonos_speakers[uid_to_join].soco)
            else:
                raise "Missing arguments"

            return True, "JOIN command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("JOIN command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_unjoin(selfself, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].unjoin()

            return True, "UNJOIN command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("UNJOIN command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def partymode(self, ip, arguments):
        try:

            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speaker[uid].partymode()

            return True, "PARTYMODE command was processed successfully."

        except Exception as err:
            return False, Exception("PARTYMODE command failed!\nException: {}".format(err))

    #ok
    def library_favradio(self, ip, arguments):
        try:
            start_item = 0
            max_items = 10

            if len(arguments) > 0:
                try:
                    start_item = int(arguments[0])
                except ValueError:
                    pass
            if len(arguments) > 1:
                try:
                    max_items = int(arguments[1])
                except ValueError:
                    pass

            return True, self.sonos_library.get_fav_radiostations(start_item, max_items)

        except Exception as err:
            return False, Exception("FAVRADIO command failed!\nException: {}".format(err))