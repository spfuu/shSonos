# -*- coding: utf-8 -*-
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

#regular expressions to find sonos meta info through udp stream

model_pattern = br'SERVER.*\((.*)\)'
uid_pattern = br'USN: uuid:(.*?):'

ip_pattern = '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
