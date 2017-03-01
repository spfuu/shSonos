# -*- coding: utf-8 -*-
import os
import tempfile

PLAYER_SEARCH = """M-SEARCH * HTTP/1.1
HOST: 239.255.255.250:reservedSSDPport
MAN: ssdp:discover
MX: 1
ST: urn:schemas-upnp-org:device:ZonePlayer:1"""

NS = {'dc': '{http://purl.org/dc/elements/1.1/}',
      'upnp': '{urn:schemas-upnp-org:metadata-1-0/upnp/}',
      '': '{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}'}

# regular expressions to find sonos meta info through udp stream
ip_pattern = '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'

VERSION_BUILDSTRING = "v1.2b1 (2017-03-01)"
VERSION = "1.2b1"

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 12900
DEFAULT_QUOTA = 200
DEFAULT_CFG = '/etc/default/sonos-broker'
DEFAULT_LOG = os.path.join(tempfile.gettempdir(), 'sonos-broker.log')
HTTP_SUCCESS = 200
HTTP_ERROR = 400
SCAN_TIMEOUT = 180
TIMESTAMP_PATTERN = "([0-5]?[0-9]):([0-5]?[0-9]):([0-5][0-9])"
MB_PLAYLIST = "#so_pl#"
SUBSCRIPTION_TIMEOUT = 240
MCAST_GRP = "239.255.255.250"
MCAST_PORT = 1900
RADIO_STATIONS = 0
RADIO_SHOWS = 1