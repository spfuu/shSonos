# -*- coding: utf-8 -*-
import re
import logging
from urllib.parse import unquote_plus
from soco.exceptions import SoCoUPnPException
from lib_sonos import sonos_speaker
from lib_sonos.sonos_library import SonosLibrary
from lib_sonos.udp_broker import UdpBroker
from lib_sonos.definitions import SCAN_TIMEOUT
from lib_sonos import utils

logger = logging.getLogger('')


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
            logger.error(err)
            return False, response

    def client_subscribe(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            port = int(arguments[0])
            UdpBroker.subscribe_client(ip, port)

            return True, 'Successfully subscribed client {}:{}'.format(ip, port)
        except Exception as err:
            logger.debug(err)
            return False, "Couldn't subscribe client {}:{}".format(ip, port)

    def client_unsubscribe(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            port = int(arguments[0])
            UdpBroker.unsubscribe_client(ip, port)
            logger.debug("client unsubscribed: {host}:{port}".format(host=ip, port=port))
            return True, 'Successfully unsubscribed client {}:{}'.format(ip, port)
        except Exception as err:
            logger.error(err)
            return False, "Couldn't unsubscribe client {}:{}".format(ip, port)

    def client_list(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            data = ''
            for uid, speaker in sonos_speaker.sonos_speakers.items():
                data += "<p>uid             : {}</p>".format(speaker.uid)
                data += "<p>ip              : {}</p>".format(speaker.ip)
                data += "<p>model           : {}</p>".format(speaker.model)
                data += "<p>current zone    : {}</p>".format(speaker.zone_name)
                data += "<p>-------------------------------------------</p><p></p><p></p>"

                logger.debug("active speakers: {uid} | {ip} | {model} | {zone}".
                             format(uid=speaker.uid, ip=speaker.ip, model=speaker.model, zone=speaker.zone_name))
            if not data:
                logger.debug('no speakers online')
                data = "No speakers online! Discover scan is performed every {} seconds.".format(SCAN_TIMEOUT)

            return True, data
        except Exception as err:
            logger.error(err)
            return False, "Couldn't list speakers"

    def speaker_current_state(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].send_data(force=True)

            return True, "CURRENTSTATE command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            logger.error(err)
            return False, Exception(
                "CURRENTSTATE command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_trackinfo(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].track_info()
            sonos_speaker.sonos_speakers[uid].send_data()

            return True, "TRACKINFO command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception(
                "TRACKINFO command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_play_uri(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:
                uri = unquote_plus(arguments[1])
                uri = utils.url_fix(uri)
                sonos_speaker.sonos_speakers[uid].play_uri(uri.decode())
            else:
                raise Exception("Missing arguments")

            # we need no explicit response here, play uri event triggers the update
            return True, "PLAYURI command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("PLAYURI command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_play_snippet(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
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

            # we need no explicit response here, playsnippet event triggers the update

            return True, "PLAYSNIPPET command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception(
                "PLAYSNIPPET command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_play_tts(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))

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
                                                       self.sonos_service.local_share, language,
                                                       self.sonos_service.quota)
            # we need no explicit response here, playtts event triggers the update

            return True, "PLAYTTS command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("PLAYTTS command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_next(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].next()

            # we need no explicit response here, next title event triggers the update

            return True, "NEXT command was processed successfully for speaker with uid '{}'.".format(uid)

        except SoCoUPnPException as err:
            if err.error_code != '711':
                return False, Exception(
                    "NEXT command failed for speaker with uid '{}'!\nException: {}".format(uid, err))
            else:
                # illegal seek action, no more items in playlist, uncritical
                return True, "NEXT command was processed successfully for speaker with uid '{}'.".format(uid)
        except Exception as err:
            return False, Exception("NEXT command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_previous(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].previous()

            # we need no explicit response here, previous title event triggers the update

            return True, "PREVIOUS command was processed successfully for speaker with uid '{}'.".format(uid)

        except SoCoUPnPException as err:
            if err.error_code != '711':
                return False, Exception(
                    "PREVIOUS command failed for speaker with uid '{}'!\nException: {}".format(uid, err))
            else:
                # illegal seek action, no more items in playlist, uncritical
                return True, "PREVIOUS command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception(
                "PREVIOUS command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_seek(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:
                timestamp = arguments[1]
                sonos_speaker.sonos_speakers[uid].seek(timestamp)

            # we need no explicit response here, next title event triggers the update

            return True, "SEEK command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("SEEK command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_stop(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:
                value = arguments[1].lower()
                if value == '1':
                    sonos_speaker.sonos_speakers[uid].stop = True
                elif value == '0':
                    sonos_speaker.sonos_speakers[uid].stop = False
                else:
                    raise Exception('Unknown parameter {value} for STOP command!'.format(value=value))
            else:
                sonos_speaker.sonos_speakers[uid].stop = not sonos_speaker.sonos_speakers[uid].stop

            # we need no explicit response here, stop event triggers the update

            return True, "STOP command was processed successfully for speaker with uid '{}'.".format(uid)

        except SoCoUPnPException as err:
            if err.error_code != '701':
                return False, Exception(
                    "STOP command failed for speaker with uid '{}'!\nException: {}".format(uid, err))
            else:
                # 701 happens, if no title is in current playlist
                return True, "STOP command was processed successfully for speaker with uid '{}'.".format(uid)
        except Exception as err:
            return False, Exception(
                "STOP command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_play(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:
                value = arguments[1].lower()
                if value == '1':
                    sonos_speaker.sonos_speakers[uid].play = True
                elif value == '0':
                    sonos_speaker.sonos_speakers[uid].play = False
                else:
                    raise Exception('Unknown parameter {value} for PLAY command!'.format(value=value))
            else:
                sonos_speaker.sonos_speakers[uid].play = not sonos_speaker.sonos_speakers[uid].play

            # we need no explicit response here, play event triggers the update

            return True, "PLAY command was processed successfully for speaker with uid '{}'.".format(uid)

        except SoCoUPnPException as err:
            if err.error_code != '701':
                return False, Exception(
                    "PLAY command failed for speaker with uid '{}'!\nException: {}".format(uid, err))
            else:
                # 701 happens, if no title is in current playlist
                # we're setting stop to 1
                status = logger.warning("No items in playlist. Setting STOP for speaker with uid to 1'{}'.".format(uid))
                sonos_speaker.sonos_speakers[uid].stop = 1
                return True, status
        except Exception as err:
            return False, Exception(
                "PLAY command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_pause(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            # some sonos specific adjustments here:
            # if a radio stream is played, the pause function is internally handled as a stop command
            # we're doing the same

            if len(arguments) > 1:
                value = arguments[1].lower()
                if value == '1':
                    value = True
                elif value == '0':
                    value = False
                else:
                    raise Exception('Unknown parameter {value} for PAUSE command!'.format(value=value))
            else:
                if sonos_speaker.sonos_speakers[uid].streamtype == 'radio':
                    value = not sonos_speaker.sonos_speakers[uid].stop
                else:
                    value = not sonos_speaker.sonos_speakers[uid].pause

            if sonos_speaker.sonos_speakers[uid].streamtype == 'radio':
                sonos_speaker.sonos_speakers[uid].stop = value
            else:
                sonos_speaker.sonos_speakers[uid].pause = value

            # we need no explicit response here, pause event triggers the update

            return True, "PAUSE command was processed successfully for speaker with uid '{}'.".format(uid)

        except SoCoUPnPException as err:
            if err.error_code != '701':
                return False, Exception(
                    "PAUSE command failed for speaker with uid '{}'!\nException: {}".format(uid, err))
            else:
                # 701 happens, if no title is in current playlist
                return True, "PAUSE command was processed successfully for speaker with uid '{}'.".format(uid)
        except Exception as err:
            return False, Exception(
                "PAUSE command failed for speaker with uid '{}'!\nException: {}".format(uid, err))


    def speaker_mute(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:
                value = arguments[1].lower()
                if value == '1':
                    sonos_speaker.sonos_speakers[uid].mute = True
                elif value == '0':
                    sonos_speaker.sonos_speakers[uid].mute = False
                else:
                    raise Exception('Unknown parameter {value} for MUTE command!'.format(value=value))
            else:
                sonos_speaker.sonos_speakers[uid].mute = not sonos_speaker.sonos_speakers[uid].mute

            # we need no explicit response here, mute event triggers the update
            return True, "MUTE command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("MUTE command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_led(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:
                value = arguments[1].lower()
                if value == '1':
                    sonos_speaker.sonos_speakers[uid].led = True
                elif value == '0':
                    sonos_speaker.sonos_speakers[uid].led = False
                else:
                    raise Exception('Unknown parameter {value} for LED command!'.format(value=value))
            else:
                sonos_speaker.sonos_speakers[uid].led = not sonos_speaker.sonos_speakers[uid].led

            sonos_speaker.sonos_speakers[uid].send_data()

            return True, "LED command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("LED command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_volume_up(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].volume_up()

            # we need no explicit response here, volume up event triggers the update
            return True, "VOLUME_UP command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception(
                "VOLUME_UP command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_volume_down(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].volume_down()

            # we need no explicit response here, volume down event triggers the update
            return True, "VOLUME_DOWN command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception(
                "VOLUME_DOWN command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_volume(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:
                value = int(arguments[1])
                sonos_speaker.sonos_speakers[uid].volume = value

            # we need no explicit response here, volume event triggers the update
            return True, "VOLUME command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("VOLUME command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_maxvolume(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:
                value = int(arguments[1])
                sonos_speaker.sonos_speakers[uid].max_volume = value

            sonos_speaker.sonos_speakers[uid].send_data()

            return True, "MAXVOLUME command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception(
                "MAXVOLUME command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_join(selfself, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
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
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speakers[uid].unjoin()

            return True, "UNJOIN command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("UNJOIN command failed for speaker with uid '{}'!\nException: {}".format(uid, err))

    def speaker_bass(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:
                value = int(arguments[1])
                if not utils.check_bass_range(value):
                    raise Exception('Bass has to be a value between -10 and 10!')
                sonos_speaker.sonos_speakers[uid].bass = value

            # we need no explicit response here, bass event triggers the update
            return True, "BASS command was processed successfully."

        except Exception as err:
            return False, Exception("BASS command failed!\nException: {}".format(err))

    def speaker_treble(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:
                value = int(arguments[1])
                if not utils.check_treble_range(value):
                    raise Exception('Treble has to be a value between -10 and 10!')
                sonos_speaker.sonos_speakers[uid].treble = value

            # we need no explicit response here, treble event triggers the update
            return True, "TREBLE command was processed successfully."

        except Exception as err:
            return False, Exception("TREBLE command failed!\nException: {}".format(err))

    def speaker_loudness(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:
                value = arguments[1].lower()
                if value == '1':
                    sonos_speaker.sonos_speakers[uid].loudness = True
                elif value == '0':
                    sonos_speaker.sonos_speakers[uid].loudness = False
                else:
                    raise Exception('Unknown parameter {value} for LOUDNESS command!'.format(value=value))
            else:
                sonos_speaker.sonos_speakers[uid].loudness = not sonos_speaker.sonos_speakers[uid].loudness

            # we need no explicit response here, loudness event triggers the update

            return True, "LOUDNESS command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("LOUDNESS command failed!\nException: {}".format(err))

    def speaker_playmode(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            uid = arguments[0].lower()

            valid = ['normal', 'shuffle_norepeat', 'shuffle', 'repeat_all']

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            if len(arguments) > 1:
                value = arguments[1].lower()

                if value not in valid:
                    raise Exception(
                        'Unknown parameter {value} for PLAYMODE command!\nValid options: {valid}'.format(value=value,
                                                                                                         valid=valid))
                else:
                    sonos_speaker.sonos_speakers[uid].playmode = value
            else:
                sonos_speaker.sonos_speakers[uid].playmode = 'normal'

            # we need no explicit response here, playmode event triggers the update

            return True, "PLAYMODE command was processed successfully for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, Exception("PLAYMODE command failed!\nException: {}".format(err))

    def partymode(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
            uid = arguments[0].lower()

            if not uid in sonos_speaker.sonos_speakers:
                raise Exception("Couldn't find any speaker with uid '%s'!" % uid)

            sonos_speaker.sonos_speaker[uid].partymode()

            return True, "PARTYMODE command was processed successfully."

        except Exception as err:
            return False, Exception("PARTYMODE command failed!\nException: {}".format(err))

    def library_favradio(self, ip, arguments):
        try:
            logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))
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
