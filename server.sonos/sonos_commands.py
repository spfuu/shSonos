import argparse
import re

import sys
#sys.path.append('/usr/smarthome/plugins/sonos/server/pycharm-debug-py3k.egg')
#import pydevd


class Command():

    def __init__(self, service):
        self.sonos_service = service
        self.true_vars = ['true', '1', 't', 'y', 'yes']

    def do_work(self, client_ip, path):

        response = 'Unknown command'
        try:
            print(client_ip)
            command = path.lower()
            command = re.sub("^/|/$", '', command).split('/')

            if command[0].lower() == 'speaker':
                " input is : speaker/uid/property/action/value" \
                " we're changing uid with property to get better handling with slices"

                c1 = command[1]
                c2 = command[2]

                command[1] = c2
                command[2] = c1

            if command:
                do_work = getattr(self, "{}_{}".format(command[0], command[1]))
                return do_work(client_ip, command[2:])
        except:
            return False, response

    def client_subscribe(self, ip, arguments):
        try:
            port = int(arguments[0])
            self.sonos_service.udp_broker.subscribe_client(ip, port)
            return True, 'Successfully subscribed client {}:{}'.format(ip, port)
        except:
            return False, "Couldn't subscribe client {}:{}".format(ip, port)

    def client_unsubscribe(self, ip, arguments):
        try:
            port = int(arguments[0])
            self.sonos_service.udp_broker.unsubscribe_client(ip, port)
            return True, 'Successfully unsubscribed client {}:{}'.format(ip, port)
        except:
            return False, "Couldn't unsubscribe client {}:{}".format(ip, port)

    def client_list(self, ip, arguments):
        try:
            speakers = self.sonos_service.get_speakers()

            data = ''

            for uid, speaker in speakers.items():
                data += "<p>uid   : {}</p>".format(speaker.uid)
                data += "<p>ip    : {}</p>".format(speaker.ip)
                data += "<p>model : {}</p>".format(speaker.model)
                data += "<p>-------------------------------------------</p><p></p><p></p>"

            if not data:
                data = "no speakers online!"

            return True, data
        except:
            return False, "Couldn't list speakers"

    def speaker_mute(self, ip, arguments):
        print(arguments)
        uid = arguments[0].lower()
        action = arguments[1]

        soco = self.sonos_service.get_soco(uid)

        if not soco:
            raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

        if action == 'set':
            try:
                value = arguments[2]
                if value in self.true_vars:
                    soco.mute = True
                else:
                    soco.mute = False

            except:
                raise Exception("Couldn't set mute status for speaker with uid '{}'!".format(uid))

        try:
            self.sonos_service.udp_broker.udp_send("speaker/{}/mute/{}".format(uid, int(soco.mute)))
            return True, "Successfully send mute command for speaker with uid '{}'.".format(uid)
        except:
            raise Exception("Couldn't get mute status for speaker with uid '{}'!".format(uid))


    def speaker_led(self, ip, arguments):
        try:
            uid = arguments[0].lower()
            action = arguments[1]

            soco = self.sonos_service.get_soco(uid)

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            if action == 'set':
                try:
                    value = arguments[2]
                    if value in self.true_vars:
                        soco.status_light = True
                    else:
                        soco.status_light = False

                except:
                    raise Exception("Couldn't set led status for speaker with uid '{}'!".format(uid))

            try:
                self.sonos_service.udp_broker.udp_send("speaker/{}/led/{}".format(uid, int(soco.status_light)))
                return True, "Successfully send led command for speaker with uid '{}'.".format(uid)
            except Exception as err:
                raise Exception("Couldn't get led status for speaker with uid '{}'!".format(uid))

        except Exception as err:
            return False, err

    def speaker_volume(self, ip, arguments):
        try:
            uid = arguments[0].lower()
            action = arguments[1]

            soco = self.sonos_service.get_soco(uid)

            if not soco:
                raise Exception("Couldn't find speaker with uid '{}'!".format(uid))

            if action == 'set':
                try:
                    value = arguments[2]
                    check_volume_range(value)
                    soco.volume = value

                except:
                    raise Exception("Couldn't set volume for speaker with uid '{}'!".format(uid))

            try:
                self.sonos_service.udp_broker.udp_send("speaker/{}/volume/{}".format(uid, int(soco.volume)))
                return True, "Successfully send volume command for speaker with uid '{}'.".format(uid)
            except Exception:
                raise Exception("Couldn't get volume for speaker with uid '{}'!".format(uid))

        except Exception as err:
            return False, err


def check_volume_range(volume):
    value = int(volume)

    if value < 0 or value > 100:
        msg = 'Volume has to be between 0 and 100.'
        raise argparse.ArgumentTypeError(msg)

    return value
