# -*- coding: utf-8 -*-
import re
import urllib
from urllib.parse import unquote_plus
from lib_sonos import sonos_speaker
from lib_sonos.sonos_library import SonosLibrary
from lib_sonos.udp_broker import UdpBroker
from lib_sonos.sonos_service import SonosServerService


class Command():
    def __init__(self, service):
        self.sonos_service = service
        self.sonos_library = SonosLibrary()
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
            speakers = SonosServerService.get_speakers()
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

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:

                if arguments[1] in self.true_vars:
                    sonos_speaker.sonos_speakers[uid].set_stop(True)
                else:
                    sonos_speaker.sonos_speakers[uid].set_stop(False)

            sonos_speaker.sonos_speakers[uid].send_data()

            return True, "STOP command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("STOP command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_play(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:

                if arguments[1] in self.true_vars:
                    sonos_speaker.sonos_speakers[uid].set_play(True)
                else:
                    sonos_speaker.sonos_speakers[uid].set_play(False)

            sonos_speaker.sonos_speakers[uid].send_data()

            return True, "PLAY command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("PLAY command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_pause(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:

                if arguments[1] in self.true_vars:
                    sonos_speaker.sonos_speakers[uid].set_pause(True)
                else:
                    sonos_speaker.sonos_speakers[uid].set_pause(False)

            sonos_speaker.sonos_speakers[uid].send_data()

            return True, "PAUSE command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("PAUSE command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_mute(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:

                if arguments[1] in self.true_vars:
                    sonos_speaker.sonos_speakers[uid].set_mute(True)
                else:
                    sonos_speaker.sonos_speakers[uid].set_mute(False)

            sonos_speaker.sonos_speakers[uid].send_data()

            return True, "MUTE command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("MUTE command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_led(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:

                if arguments[1] in self.true_vars:
                    sonos_speaker.sonos_speakers[uid].set_led(True)
                else:
                    sonos_speaker.sonos_speakers[uid].set_led(False)

            sonos_speaker.sonos_speakers[uid].send_data()

            return True, "LED command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("LED command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_volume(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:
                value = int(arguments[1])
                sonos_speaker.sonos_speakers[uid].set_volume(value)

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
                sonos_speaker.sonos_speakers[uid].set_maxvolume(value)

            sonos_speaker.sonos_speakers[uid].send_data()

            return True, "MAXVOLUME command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("MAXVOLUME command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_next(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].set_next()

            #we need no explicit response here, next title event triggers the update

            return True, "NEXT command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("NEXT command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_previous(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].set_previous()

            #we need no explicit response here, previous title event triggers the update

            return True, "PREVIOUS command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("PREVIOUS command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_seek(self, ip, arguments):
        try:
            uid = arguments[0].lower()
            action = ''

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 2:
                action = arguments[1]

            if action == 'set':
                timestamp = arguments[2]
                sonos_speaker.sonos_speakers[uid].set_seek(timestamp)

            #we need no explicit response here, next title event triggers the update

            return True, "SEEK command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("SEEK command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_current_state(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].send_data()

            return True, "CURRENTSTATE command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("CURRENTSTATE command failed for speaker with uid '{}'!\nException: {}".format(uid, err))


    def speaker_trackinfo(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].get_track_info()
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
                uri = url_fix(uri)
                sonos_speaker.sonos_speakers[uid].set_play_uri(uri.decode())
            else:
                raise "Missing arguments"

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
                uri = url_fix(uri)
            else:
                raise "Missing arguments"

            if len(arguments) > 2:
                volume = int(arguments[2])
                if volume < -1 or volume > 100:
                    volume = -1

            sonos_speaker.sonos_speakers[uid].set_play_snippet(uri.decode(), volume)

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
                raise "Missing arguments"


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

            sonos_speaker.sonos_speakers[uid].set_play_tts(tts, volume, self.sonos_service.smb_url,
                                                           self.sonos_service.local_share, language, self.sonos_service.quota)
            #we need no explicit response here, playtts event triggers the update

            return True, "PLAYTTS command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("PLAYTTS command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_streamtype(self, ip, arguments):
        try:
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].send_data()

            return True, "STREAMTYPE command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("STREAMTYPE command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

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

def url_fix(s, charset='utf-8'):
    """Sometimes you get an URL by a user that just isn't a real
    URL because it contains unsafe characters like ' ' and so on.  This
    function can fix some of the problems in a similar way browsers
    handle data entered by the user:

    'http://de.wikipedia.org/wiki/Elf%20%28Begriffskl%C3%A4rung%29'

    :param charset: The target charset for the URL if the url was
                    given as unicode string.
    """
    if isinstance(s, str):
        s = s.encode(charset, 'ignore')
    scheme, netloc, path, query, fragment = urllib.parse.urlsplit(s)
    path = urllib.parse.quote(path, '/%').encode(charset)
    query = urllib.parse.quote_plus(query, ':&=').encode(charset)
    return urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))