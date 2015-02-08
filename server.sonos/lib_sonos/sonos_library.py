from lib_sonos import sonos_speaker
from lib_sonos import utils


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