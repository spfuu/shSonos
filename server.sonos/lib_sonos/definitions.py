# -*- coding: utf-8 -*-
import os
import tempfile

__author__ = 'pfischi'

PLAYER_SEARCH = """M-SEARCH * HTTP/1.1
HOST: 239.255.255.250:reservedSSDPport
MAN: ssdp:discover
MX: 1
ST: urn:schemas-upnp-org:device:ZonePlayer:1"""

MCAST_GRP = "239.255.255.250"
MCAST_PORT = 1900

RADIO_STATIONS = 0
RADIO_SHOWS = 1

NS = {'dc': '{http://purl.org/dc/elements/1.1/}',
      'upnp': '{urn:schemas-upnp-org:metadata-1-0/upnp/}',
      '': '{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}'}

# regular expressions to find sonos meta info through udp stream
ip_pattern = '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'

VERSION = "v0.7 (2016-01-04)"

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 12900
DEFAULT_QUOTA = 100
DEFAULT_CFG = 'sonos_broker.cfg'
DEFAULT_LOG = os.path.join(tempfile.gettempdir(), 'sonos_broker.log')
DEFAULT_PID = os.path.join(tempfile.gettempdir(), 'sonos_broker.pid')
HTTP_SUCCESS = 200
HTTP_ERROR = 400
SCAN_TIMEOUT = 180
TIMESTAMP_PATTERN = "([0-5]?[0-9]):([0-5]?[0-9]):([0-5][0-9])"
MB_PLAYLIST = "#so_pl#"
SUBSCRIPTION_TIMEOUT = 240
