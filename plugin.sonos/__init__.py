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
import http

import logging
import lib.connection
import lib.tools

#for remote debugging only##import sys
#sys.path.append('/usr/smarthome/plugins/sonos/pycharm-debug-py3k.egg')
#import pydevd

logger = logging.getLogger('Sonos')


class UDPDispatcher(lib.connection.Server):

    def __init__(self, parser, ip, port):
        lib.connection.Server.__init__(self, ip, port, proto='UDP')
        self.dest = 'udp:' + ip + ':' + port
        self.parser = parser
        self.connect()

    def handle_connection(self):
        try:
            data, addr = self.socket.recvfrom(4096)
            ip = addr[0]
            addr = "{}:{}".format(addr[0], addr[1])
            logger.debug("{}: incoming connection from {}".format(self._name, addr))
        except Exception as e:
            logger.exception("{}: {}".format(self._name, e))
            return

        self.parser(ip, self.dest, data.decode().strip())

class Sonos():

    def __init__(self, smarthome, host='0.0.0.0', port='9999', broker_url=None):

        #pydevd.settrace('192.168.178.44', port=12000, stdoutToServer=True, stderrToServer=True)

        if broker_url:
            self._broker_url = broker_url

        self.send_cmd('client/subscribe/{}'.format(port))
        self._sh = smarthome
        self.command = SonosCommand()
        self._val = {}

        UDPDispatcher(self.parse_input, host, port)

    def parse_input(self, source, dest, data):
        try:
           values = data.split('\n')
           for value in values:
                logger.debug(value)
                self.update_items_with_data(value)

        except Exception as err:
            logger.debug(err)

    def run(self):
        self.alive = True
        # if you want to create child threads, do not make them daemon = True!
        # They will not shutdown properly. (It's a python bug)

    def stop(self):
        self.alive = False

    def resolve_cmd(self, item, attr):
        if '<sonos_uid>' in item.conf[attr]:
            parent_item = item.return_parent()
            if (parent_item is not None) and ('sonos_uid' in parent_item.conf):
                item.conf[attr] = item.conf[attr].replace('<sonos_uid>', parent_item.conf['sonos_uid'].lower())
            else:
                logger.warning("sonos: could not resolve sonos_uid".format(item))
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
            value = item()

            if 'sonos_send' in item.conf:
                cmd = self.resolve_cmd(item, 'sonos_send')

                if not cmd:
                    return None

                command = self.split_command(cmd)

                #command[0] = speaker / zone? / group?
                #command[1] = uid
                #command[2..n] = command to execute

                if command[2] == 'mute':
                    if isinstance(value, bool):
                        cmd = self.command.mute(command[1], int(value))
                if command[2] == 'led':
                    if isinstance(value, bool):
                        cmd = self.command.led(command[1], int(value))
                if command[2] == 'volume':
                    if isinstance(value, int):
                        cmd = self.command.volume(command[1], int(value))

                if cmd:
                    self.send_cmd(cmd)
        else:
            logger.debug("SONOS CALLER")
        return None

    @staticmethod
    def split_command(cmd):
        return cmd.lower().split('/')

    def send_cmd(self, cmd):

        try:
            conn = http.client.HTTPConnection(self._broker_url)

            conn.request("GET", cmd)
            response = conn.getresponse()
            if response.status == 200:
                logger.info("Sonos: Message %s %s successfully sent - %s %s" %
                            (self._broker_url, cmd, response.status, response.reason))
            else:
                logger.warning("Sonos: Could not send message %s %s - %s %s" %
                               (self._broker_url, cmd, response.status, response.reason))
            conn.close()
            del(conn)

        except Exception as e:
            logger.warning(
                "Could not send sonos notification: {0}. Error: {1}".format(cmd, e))

        logger.debug("Sending request: {0}".format(cmd))



    def update_items_with_data(self, data):

        #trim the last occurence of '/': everything right-hand-side is our value
        cmd = data.rsplit('/', 1)

        if cmd[0] in self._val:
            for item in self._val[cmd[0]]['items']:
                if isinstance(item(), str):
                    cmd[1] = int(cmd[1]) + item()
                logger.debug("data: {}".format(cmd[1]))
                item(cmd[1], 'Sonos', '')

class SonosCommand():
    @staticmethod
    def mute(uid, value):
        return "speaker/{}/mute/set/{}".format(uid, int(value))

    @staticmethod
    def led(uid, value):
        return "speaker/{}/led/set/{}".format(uid, int(value))

    @staticmethod
    def volume(uid, value):
        return "speaker/{}/volume/set/{}".format(uid, value)

    @staticmethod
    def get_uid_from_response(dom):
        try:
            return dom.attributes["uid"].value.lower()
        except:
           return None

    @staticmethod
    def get_bool_result(dom, result_string):
        try:
            node = dom.getElementsByTagName(result_string)
            if not node:
                return None
            value = node[0].childNodes[0].nodeValue.lower()

            if value in ['true', '1', 't', 'y', 'yes']:
                return True
            return False
        except:
            return None


