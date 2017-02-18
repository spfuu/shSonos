import logging
from lib_sonos import sonos_speaker
from lib_sonos import utils

logger = logging.getLogger('sonos_broker')

class SonosLibrary:

    @classmethod
    def get_fav_radiostations(cls, start_item, max_items):

        # get any speaker in our list

        stations = {}
        found = False

        for key, value in sonos_speaker.sonos_speakers.items():
            try:
                soco = sonos_speaker.sonos_speakers[key].soco
                stations = soco.get_favorite_radio_stations(start_item, max_items)
                found = True
                break
            except Exception:
                pass

        if not found:
            raise Exception("Couldn't fetch favorite radio stations. All speakers offline?")

        return utils.to_json(stations)


    @classmethod
    def refresh_media_library(cls, album_artist_display_option=''):

        found = False

        logger.debug(album_artist_display_option)

        for key, value in sonos_speaker.sonos_speakers.items():
            soco = sonos_speaker.sonos_speakers[key].soco

            logger.debug("!!!!!!!!!!!!!!!! %s " % soco.library_updating)
            if soco.library_updating:
                raise Exception("Media library is already updating. Try later!")

            soco.start_library_update(album_artist_display_option)
            found = True
            break

        if not found:
            raise Exception("Couldn't refresh media library. All speakers offline?")