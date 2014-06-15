from lib_sonos import sonos_speaker
from lib_sonos import utils

class SonosLibrary:
    def __init__(self):
        pass

    def get_fav_radiostations(self, start_item, max_items):

        #get at least one ip from our online speakers
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