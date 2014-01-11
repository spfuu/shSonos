#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2013 KNX-User-Forum e.V. http://knx-user-forum.de/
#########################################################################
# This file is part of SmartHome.py. http://mknx.github.io/smarthome/
#
# SmartHome.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SmartHome.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import lib.connection
from xml.dom import minidom

logger = logging.getLogger('Sonos')

RESPDELIMITER = b'</result>'


class Sonos(lib.connection.Client):
    def __init__(self, smarthome, host='127.0.0.1', port='9999'):
        lib.connection.Client.__init__(self, host, port, monitor=True)
        self._sh = smarthome
        self.terminator = RESPDELIMITER
        self.command = SonosCommand()
        self._val = {}

    def run(self):
        self.alive = True
        # if you want to create child threads, do not make them daemon = True!
        # They will not shutdown properly. (It's a python bug)

    def stop(self):
        self.alive = False

    def resolve_cmd(self, item, attr):
        if '<sonos_uid>' in item.conf[attr]:
            uid = self.get_sonos_uid(item)

            if uid:
                item.conf[attr] = item.conf[attr].replace('<sonos_uid>', uid)
            else:
                logger.warning(
                    "sonos: could not resolve sonos_uid for {0} from parent item {1}".format(item, parent_item))

        return item.conf[attr]

    def parse_item(self, item):
        if 'sonos_recv' in item.conf:
            cmd = self.resolve_cmd(item, 'sonos_recv')

            if cmd is None:
                return None

            logger.debug("sonos: {} receives updates by {}".format(item, cmd))

            if not cmd in self._val:
                self._val[cmd] = {'items': [item], 'logics': []}
            else:
                if not item in self._val[cmd]['items']:
                    self._val[cmd]['items'].append(item)

        if 'sonos_send' in item.conf:
            logger.debug("SONOS SEND SONOS SEND SONOS SEND SONOS SEND")
            cmd = self.resolve_cmd(item, 'sonos_send')

            if cmd is None:
                return None

            logger.debug("sonos: {} is send to {}".format(item, cmd))
            return self.update_item

        return None


    #nothing yet
    def parse_logic(self, logic):
        pass

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'Sonos':
            cmd = ''

            if 'sonos_send' in item.conf:
                uid = self.get_sonos_uid(item)

                if not uid:
                    return None

                value = item()
                if isinstance(value, bool):
                    cmd = self.command.mute(uid, int(value))
            if cmd:
                self.send_cmd(cmd)
        else:
            logger.debug("SONOS CALLER")
        return None

    def get_sonos_uid(self, item):
        parent_item = item.return_parent()

        if (parent_item is not None) and ('sonos_uid' in parent_item.conf):
            return parent_item.conf['sonos_uid'].lower()
        logger.warning("sonos: could not resolve sonos uid")
        return None

    def send_cmd(self, cmd):
        logger.debug("Sending request: {0}".format(cmd))

        # if connection is closed we don't wait for sh.con to reopen it
        # instead we reconnect immediatly
        if not self.connected:
            self.connect()

        self.send(cmd)

    def found_terminator(self, resp):
        #data = urllib.parse.unquote(resp)
        data = resp.decode('utf-8')
        terminator = self.terminator.decode('utf-8')

        #we're using xml, add the terminator again, its the closing tag
        data = "{}{}".format(data, terminator)
        logger.debug(data)

        try:
            dom = minidom.parseString(data).documentElement
            uid = self.command.get_uid_from_response(dom)
            value = self.command.get_bool_result(dom, 'mute')

            if value:
                self.update_items_with_data(["{} mute".format(uid), int(value)])

        except Exception as err:
            logger.debug(err)

    def update_items_with_data(self, data):
        cmd = ' '.join(data_str for data_str in data[:-1])
        if (cmd in self._val):
            for item in self._val[cmd]['items']:
                if isinstance(item(), str):
                    data[-1] = int(data[-1]) + item()
                logger.debug("data[-1]: {}".format(data[-1]))
                item(data[-1], 'Sonos', self.address)

    def handle_connect(self):
        self.discard_buffers()
        self.terminator = RESPDELIMITER


class SonosCommand():

    @staticmethod
    def normalize(cmd):
        return bytes("{}\r\n".format(cmd), encoding='utf-8')


    @staticmethod
    def get_uid_from_response(dom):
        try:
            return dom.attributes["uid"].value
        except:
            return None

    @staticmethod
    def get_bool_result(dom, result_string):
        try:
            node = dom.getElementsByTagName('mute')
            if not node:
                return None
            value = node[0].childNodes[0].nodeValue.lower()

            if value in ['true', '1', 't', 'y', 'yes']:
                return True
            return False
        except:
            return None

    def mute(self, uid, value):
        return self.normalize("speaker mute {} {}".format(int(value), uid))
