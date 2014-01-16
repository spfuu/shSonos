import argparse
import re
import sys
from udp_broker import UdpBroker
from xml_formatter import xml_format_status

#sys.path.append('/usr/smarthome/plugins/sonos/server/pycharm-debug-py3k.egg')
#import pydevd


class Command():

    def __init__(self, service):
        self.sonos_service = service
        self.true_vars = ['true', '1', 't', 'y', 'yes']
        self.udp_broker = UdpBroker()


    def do_work(self, client_ip, path):

        response = 'Unknown command'
        try:
            print(client_ip)
            command = path.lower()
            command = re.sub("^/|/$", '', command).split('/')

            if command:
                try:
                    do_work = getattr(self, command[0])
                    return do_work(client_ip, command[1:])

                except:
                    pass
        except:
            pass

        return False, response

    def subscribe(self, ip, arguments):
        try:
            port = int(arguments[0])
            self.udp_broker.subscribe_client(ip, port)
            return True, 'Successfully subscribed client {}:{}'.format(ip, port)
        except:
            return False, "Couldn't subscribe client {}:{}".format(ip, port)

    def unsubscribe(self, ip, arguments):
        try:
            port = int(arguments[0])
            self.udp_broker.unsubscribe_client(ip, port)
            return True, 'Successfully unsubscribed client {}:{}'.format(ip, port)
        except:
            return False, "Couldn't unsubscribe client {}:{}".format(ip, port)

    def mute(self, ip, arguments):
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
                        soco.mute = True
                    else:
                        soco.mute = False

                    self.udp_broker.udp_send(xml_format_status(True, uid, '', dict(mute=soco.mute)))
                    return True, "Successfully send mute command for speaker with uid '{}'.".format(uid)

                except:
                    raise Exception("Couldn't set mute status for speaker with uid '{}'!".format(uid))

            if action == 'get':
                self.udp_broker.udp_send(xml_format_status(True, uid, '', dict(mute=soco.mute)))
                return True, "Successfully send mute command for speaker with uid '{}'.".format(uid)

        except Exception as err:
            return False, err


def check_volume_range(volume):
    value = int(volume)

    if value < 0 or value > 100:
        msg = 'Volume has to be between 0 and 100.'
        raise argparse.ArgumentTypeError(msg)

    return value

# ""class GCommand():
#     def __init__(self, command, database):
#         i = 110
#
#     def speakers_refresh(self, args=None):
#
#         """internal method for a quick refresh of all sonos speakers in the network"""
#         speakers = self.sonos_service.get_speakers()
#         self.database.set_speakers_offline()
#
#         for speaker in speakers:
#             self.database.add_speaker(speaker)
#
#     def speakers_refresh_quick(self, args=None):
#         """ refresh devices (ip, model, online/offline status, uuid) """
#         try:
#             self.speakers_refresh()
#             return xml_format_status(True)
#         except Exception as err:
#             return xml_format_exception(err)
#
#     def speakers_refresh_all(self, args=None):
#
#         try:
#             self.speakers_refresh()
#
#             query_options = {VwDeviceColumns.status: 1}
#             speakers = self.database.speakers_list(query_options)
#
#             count = 0
#
#             for speaker in speakers:
#                 self.speaker_refresh_detail(speaker)
#                 count += 1
#
#             return xml_format_status(True, '{} sonos speaker(s) refreshed.'.format(count))
#
#         except Exception as err:
#             return xml_format_exception(err)
#
#     def speaker_refresh_by_ip(self, args):
#         try:
#             self.speakers_refresh_quick()
#             device_ip = args.device_ip
#
# #            query_options = {VwDeviceColumns.ip: device_ip}
#  #           speakers = self.database.speakers_list(query_options)
#
#             #if speakers:
#             #    self.speaker_refresh_detail(speakers[0])
#             #    return xml_format_status(True, 'Sonos speaker with ip \'{}\' refreshed.'.format(speakers[0].ip))
#             #else:
#             #    return xml_format_status(False,
#             #                             'No sonos speaker found with ip \'{}\'. Device offline?'.format(device_ip))
#
#         except Exception as err:
#             return xml_format_exception(err)
#
#     def speaker_refresh_by_id(self, args):
#         try:
#             self.speakers_refresh_quick()
#             device_id = args.device_id
#
#   #          query_options = {VwDeviceColumns.id: device_id}
#    #         speakers = self.database.speakers_list(query_options)
#
#     #        if speakers:
#      #           self.speaker_refresh_detail(speakers[0])
#       #          return xml_format_status(True,
#           #                               'Sonos speaker with id \'{}\' and ip \'{}\' refreshed.'.format(speakers[0].id,
#            #                                                                                             speakers[0].ip))
#        #     else:
#         #        return xml_format_status(False,
#          #                                'No sonos speaker found with id \'{}\'. Device offline?'.format(device_id))
#
#         except Exception as err:
#             return xml_format_exception(err)
#
#     def speaker_refresh_by_uid(self, args):
#         try:
#             self.speakers_refresh_quick()
#             device_uid = args.device_uid
#
#             #query_options = {VwDeviceColumns.uid: device_uid}
#             #speakers = self.database.speakers_list(query_options)
#
#             #if speakers:
#             #    self.speaker_refresh_detail(speakers[0])
#             #    return xml_format_status(True, 'Sonos speaker with uid \'{}\' and ip \'{}\' refreshed.'.format(
#             #        speakers[0].uid, speakers[0].ip))
#             #else:
#             #    return xml_format_status(False,
#              #                            'No sonos speaker found with uid \'{}\'. Device offline?'.format(device_uid))
#
#         except Exception as err:
#             return xml_format_exception(err)
#
#     def speaker_refresh_detail(self, speaker):
#         """ internal method to get detailed information about a sonos speaker """
#
#         speaker_details = self.sonos_service.get_speaker_info(speaker)
#
#         #returned speaker object does not contain all necessary data
#         speaker_details.model = speaker.model
#         speaker_details.id = speaker.id
#
#         self.database.set_speaker_info(speaker_details)
#
#     def speakers_list_all(self, arguments):
#         try:
#
#             query_options = {}
#
#             #if arguments.status == 'offline':
#              #   query_options[VwDeviceColumns.status] = 0
#             #if arguments.status == 'online':
#              #   query_options[VwDeviceColumns.status] = 1
#
#             #if complete : leave query options blank -> no where clause in selection
#
#             rows = self.database.speakers_list(query_options)
#
#             return xml_format_speaker_data(rows)
#
#         except Exception as err:
#             return xml_format_exception(err)
#
#     def speaker_list_by_ip(self, arguments):
#         try:
#
#             #query_options = {VwDeviceColumns.ip: arguments.device_ip}
#
#             #rows = self.database.speakers_list(query_options)
#
#             #return xml_format_speaker_data(rows)
#
#         except Exception as err:
#             return xml_format_exception(err)
#
#     def speaker_list_by_id(self, arguments):
#         try:
#             #query_options = {VwDeviceColumns.id: arguments.device_id}
#             #rows = self.database.speakers_list(query_options)
#
#             #return xml_format_speaker_data(rows)
#
#         except Exception as err:
#             return xml_format_exception(err)
#
#     def speaker_list_by_uid(self, arguments):
#         try:
#
#             #query_options = {VwDeviceColumns.uid: arguments.device_uid}
#
#             #rows = self.database.speakers_list(query_options)
#
#             #return xml_format_speaker_data(rows)
#
#         except Exception as err:
#             return xml_format_exception(err)
#
#
#     def speaker_property_statuslight(self, arguments):
#
#         try:
#             action = arguments.action.lower()
#             refresh = arguments.refresh
#             device_uid = arguments.device_uid
#
#             soco = self.get_soco(device_uid, refresh)
#
#             if soco:
#                 if action == 'on':
#                     soco.status_light = False
#
#                 if action == 'off':
#                     soco.status_light = True
#
#                 return xml_format_status(True, device_uid, '', dict(statuslight=soco.status_light))
#
#             return xml_format_status(False, device_uid,
#                                      'No speaker found with uid \'{}\'. Speaker offline?'.format(device_uid))
#
#         except Exception as err:
#             return xml_format_exception(err)
#
#     def speaker_property_volume(self, arguments):
#
#         try:
#             action = arguments.action
#             refresh = arguments.refresh
#             device_uid = arguments.device_uid
#             device_volume = arguments.device_volume
#
#             soco = self.get_soco(device_uid, refresh)
#
#             if soco:
#                 if action == 'set':
#
#                     if not device_volume:
#                         return xml_format_status(False, device_uid, 'No speaker volume has been set.')
#
#                     soco.volume = device_volume
#                     return xml_format_status(True, device_uid, '', dict(volume=soco.volume))
#
#                 return xml_format_status(True, device_uid, '', dict(volume=soco.volume))
#
#             return xml_format_status(False, device_uid,
#                                      'No speaker found with uid \'{}\'. Speaker offline?'.format(device_uid))
#
#         except Exception as err:
#             return xml_format_exception(err)

