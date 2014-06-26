import re
import logging

logger = logging.getLogger('')

# dictionary: pattern_station : [ pattern_track_artist_1, pattern_track_artist_2, ...]
# ALWAYS use a named group for track and artist

radio_list = {
    ## SWR3 ##
    re.compile(r"swr3*.?", re.IGNORECASE):  [re.compile(r"(?P<track>.*?)/(?P<artist>.*?)", re.IGNORECASE)],
    ## 104.6 RTL ##
    re.compile(r"104\.6 rtl*.?", re.IGNORECASE):  [re.compile(r"(?P<artist>.*)::(?P<track>.*)", re.IGNORECASE)]
}


def title_artist_parser(radio_station, track_artist):

    artist = ''
    track = track_artist
    found = False

    try:

        for pattern_station, patterns_track in radio_list.items():

            station_match = pattern_station.match(radio_station)

            if station_match:
                for pattern_track in patterns_track:
                    track_match = pattern_track.match(track_artist)

                    if track_match:
                        artist = track_match.group('artist')
                        track = track_match.group('track')
                        found = True
                        break

                break

        #no special parser, just try to split the radio string with '-'
        if not found:
            split_title = track_artist.split('-')

            if len(split_title) == 1:

                if split_title:
                    if len(split_title) == 2:
                            artist = split_title[0].strip()
                            track = split_title[1].strip()

                    # mostly this happens during commercial breaks, news, weather etc
                    if len(split_title) > 2:
                        artist = split_title[0].strip()
                        track = '-'.join(split_title[1:])

    except Exception as err:
        logger.exception(err)
    finally:
        return artist.strip().title(), track.strip().title()