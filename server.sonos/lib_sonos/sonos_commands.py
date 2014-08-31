# -*- coding: utf-8 -*-
import re
import logging
from urllib.parse import unquote_plus
from lib_sonos import sonos_speaker
from lib_sonos.sonos_library import SonosLibrary
from lib_sonos.definitions import SCAN_TIMEOUT
from lib_sonos import utils

logger = logging.getLogger('')

class Command():
    def __init__(self, service):
        self.sonos_service = service
        self.sonos_library = SonosLibrary()
        self.true_vars = ['true', '1', 't', 'y', 'yes']


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