import json

__author__ = 'pfischi'
from soco.core import SoCo
from lib_sonos import sonos_speaker

class SonosLibrary:
    def __init__(self):
        pass

    def to_JSON(self, dict):
        return json.dumps(self, default=lambda o: dict, ensure_ascii=False)

    def get_soco(self, ip):
        return SoCo(ip)

    def get_fav_radiostations(self, start_item, max_items):

        #get a least one ip from our online speakers

        stations = {}
        found = False

        for key, value in sonos_speaker.sonos_speakers.items():
            try:
                ip = sonos_speaker.sonos_speakers[key].ip
                soco = self.get_soco(ip)
                stations = soco.get_favorite_radio_stations(start_item, max_items)
                found = True
                break
            except Exception:
                pass

        if not found:
            raise Exception("Couldn't fetch favorite radio stations. All speakers offline?")

        return self.to_JSON(stations)
