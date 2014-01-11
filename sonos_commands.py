import argparse
from core import SoCo
from sonos_database import VwDeviceColumns
import shlex
import utils
from sonos_service import SonosService
from xml_formatter import xml_format_speaker_data, xml_format_exception, xml_format_status


class Command():
    def __init__(self, command, database):

        """ As a workaround, the dest-var is set with options's name
        to use it in error cases (see exception in do_work())"""

        self.base_command = ''
        self.arguments = ''

        self.database = database
        self.sonos_service = SonosService()
        self.command = shlex.split(command)

        self.parser = utils.ArgumentParser()

        subparsers = self.parser.add_subparsers(title='actions', dest='')

        " some dirty hacks here: we're using nested subparser. Unfortunately argparser " \
        " did not work properly in this case. E.g. we cannot add an option to indicate that" \
        " at least fon suboption has to be set ( and if not, an error is thrown " \
        " If dest-var is an empty string, the full help will be returned"

        par_refresh = subparsers.add_parser('refresh')
        sub_refresh = par_refresh.add_subparsers(title='refresh actions', dest='refresh')

        p_quick = sub_refresh.add_parser('quick', help='Performs a search for new sonos speakers and '
                                                       'updates the status of existing devices.')
        p_quick.set_defaults(function=self.speakers_refresh_quick)

        p_all = sub_refresh.add_parser('all')
        p_all.set_defaults(function=self.speakers_refresh_all)

        p_single = sub_refresh.add_parser('single')
        sub_single = p_single.add_subparsers(title='refresh single actions', dest='single')

        p_single_ip = sub_single.add_parser('ip')
        p_single_ip.add_argument('device_ip', help='A valid ip address for a sonos speaker within the network.')
        p_single_ip.set_defaults(function=self.speaker_refresh_by_ip)

        p_single_id = sub_single.add_parser('id')
        p_single_id.add_argument('device_id', type=int,
                                 help='A device id for a sonos speaker within the sqlite database.')
        p_single_id.set_defaults(function=self.speaker_refresh_by_id)

        p_single_uid = sub_single.add_parser('uid')
        p_single_uid.add_argument('device_uid', help='A device uid for a sonos speaker within the sqlite database.')
        p_single_uid.set_defaults(function=self.speaker_refresh_by_uid)

        par_list = subparsers.add_parser('list')
        sub_list = par_list.add_subparsers(title='list actions', dest='list')

        p_list_all = sub_list.add_parser('all')
        p_list_all.add_argument('status', choices={'online', 'offline', 'complete'})
        p_list_all.set_defaults(function=self.speakers_list_all)

        p_list_single = sub_list.add_parser('single')
        sub_list_single = p_list_single.add_subparsers(title='list single actions', dest='single')

        p_list_single_ip = sub_list_single.add_parser('ip')
        p_list_single_ip.add_argument('device_ip', help='A valid ip address for a sonos speaker within the network.')
        p_list_single_ip.set_defaults(function=self.speaker_list_by_ip)

        p_list_single_id = sub_list_single.add_parser('id')
        p_list_single_id.add_argument('device_id', type=int,
                                      help='A device id for a sonos speaker within the sqlite database.')
        p_list_single_id.set_defaults(function=self.speaker_list_by_id)

        p_list_single_uid = sub_list_single.add_parser('uid')
        p_list_single_uid.add_argument('device_uid',
                                       help='A device uid for a sonos speaker within the sqlite database.')
        p_list_single_uid.set_defaults(function=self.speaker_list_by_uid)

        par_speaker = subparsers.add_parser('speaker')
        sub_speaker = par_speaker.add_subparsers(title='speaker actions', dest='speaker')

        p_speaker_mute = sub_speaker.add_parser('mute')
        p_speaker_mute.add_argument('action', choices={0, 1}, type=int,
                                    help='Get or set the speaker\' mute status.')
        p_speaker_mute.add_argument('device_uid', help='A device uid for a sonos speaker within the sqlite database.')
        p_speaker_mute.add_argument('refresh', nargs='?', type=bool, default=False,
                                    help='Performs a quick refresh to get online / offline status of the device. ')
        p_speaker_mute.set_defaults(function=self.speaker_property_mute)

        p_speaker_light = sub_speaker.add_parser('statuslight')
        p_speaker_light.add_argument('action', choices={'on', 'off', 'get'},
                                     help='Get or set the state of the sonos status light.')
        p_speaker_light.add_argument('device_uid', help='A device uid for a sonos speaker within the sqlite database.')
        p_speaker_light.add_argument('refresh', nargs='?', type=bool, default=False,
                                     help='Performs a quick refresh to get online / offline status of the device. ')
        p_speaker_light.set_defaults(function=self.speaker_property_statuslight)

        p_speaker_volume = sub_speaker.add_parser('volume')
        p_speaker_volume.add_argument('action', choices={'set', 'get'},
                                      help='Get or set the speaker\'s volume.')

        p_speaker_volume.add_argument('device_volume', type=check_volume_range, nargs='?', default=0,
                                      help='An integer between 0 and 100.')

        p_speaker_volume.add_argument('device_uid', help='A device uid for a sonos speaker within the sqlite database.')
        p_speaker_volume.add_argument('refresh', nargs='?', type=bool, default=False,
                                      help='Performs a quick refresh to get online / offline status of the device. ')
        p_speaker_volume.set_defaults(function=self.speaker_property_volume)


    def do_work(self):
        try:
            args = self.parser.parse_args(self.command)
            return args.function(args)
        except AttributeError as err:
            print(err)

            "workaround Part II:"
            "If there's no function defined for a specific parser, an AttributeError is thrown." \
            "That's the case for an empty suboption. We're showing an appropiate help und usage " \
            "message for this"

            parser_help = self.parser.get_help_from_subparser_option(args)
            return xml_format_exception(Exception(parser_help))

        except Exception as err:
            return xml_format_exception(err)

        except SystemExit as err:
            return xml_format_exception(err)

    def speakers_refresh(self, args=None):

        """internal method for a quick refresh of all sonos speakers in the network"""
        speakers = self.sonos_service.get_speakers()
        self.database.set_speakers_offline()

        for speaker in speakers:
            self.database.add_speaker(speaker)

    def speakers_refresh_quick(self, args=None):
        """ refresh devices (ip, model, online/offline status, uuid) """
        try:
            self.speakers_refresh()
            return xml_format_status(True)
        except Exception as err:
            return xml_format_exception(err)

    def speakers_refresh_all(self, args=None):

        try:
            self.speakers_refresh()

            query_options = {VwDeviceColumns.status: 1}
            speakers = self.database.speakers_list(query_options)

            count = 0

            for speaker in speakers:
                self.speaker_refresh_detail(speaker)
                count += 1

            return xml_format_status(True, '{} sonos speaker(s) refreshed.'.format(count))

        except Exception as err:
            return xml_format_exception(err)

    def speaker_refresh_by_ip(self, args):
        try:
            self.speakers_refresh_quick()
            device_ip = args.device_ip

            query_options = {VwDeviceColumns.ip: device_ip}
            speakers = self.database.speakers_list(query_options)

            if speakers:
                self.speaker_refresh_detail(speakers[0])
                return xml_format_status(True, 'Sonos speaker with ip \'{}\' refreshed.'.format(speakers[0].ip))
            else:
                return xml_format_status(False,
                                         'No sonos speaker found with ip \'{}\'. Device offline?'.format(device_ip))

        except Exception as err:
            return xml_format_exception(err)

    def speaker_refresh_by_id(self, args):
        try:
            self.speakers_refresh_quick()
            device_id = args.device_id

            query_options = {VwDeviceColumns.id: device_id}
            speakers = self.database.speakers_list(query_options)

            if speakers:
                self.speaker_refresh_detail(speakers[0])
                return xml_format_status(True,
                                         'Sonos speaker with id \'{}\' and ip \'{}\' refreshed.'.format(speakers[0].id,
                                                                                                        speakers[0].ip))
            else:
                return xml_format_status(False,
                                         'No sonos speaker found with id \'{}\'. Device offline?'.format(device_id))

        except Exception as err:
            return xml_format_exception(err)

    def speaker_refresh_by_uid(self, args):
        try:
            self.speakers_refresh_quick()
            device_uid = args.device_uid

            query_options = {VwDeviceColumns.uid: device_uid}
            speakers = self.database.speakers_list(query_options)

            if speakers:
                self.speaker_refresh_detail(speakers[0])
                return xml_format_status(True, 'Sonos speaker with uid \'{}\' and ip \'{}\' refreshed.'.format(
                    speakers[0].uid, speakers[0].ip))
            else:
                return xml_format_status(False,
                                         'No sonos speaker found with uid \'{}\'. Device offline?'.format(device_uid))

        except Exception as err:
            return xml_format_exception(err)

    def speaker_refresh_detail(self, speaker):
        """ internal method to get detailed information about a sonos speaker """

        speaker_details = self.sonos_service.get_speaker_info(speaker)

        #returned speaker object does not contain all necessary data
        speaker_details.model = speaker.model
        speaker_details.id = speaker.id

        self.database.set_speaker_info(speaker_details)

    def speakers_list_all(self, arguments):
        try:

            query_options = {}

            if arguments.status == 'offline':
                query_options[VwDeviceColumns.status] = 0
            if arguments.status == 'online':
                query_options[VwDeviceColumns.status] = 1

            #if complete : leave query options blank -> no where clause in selection

            rows = self.database.speakers_list(query_options)

            return xml_format_speaker_data(rows)

        except Exception as err:
            return xml_format_exception(err)

    def speaker_list_by_ip(self, arguments):
        try:

            query_options = {VwDeviceColumns.ip: arguments.device_ip}

            rows = self.database.speakers_list(query_options)

            return xml_format_speaker_data(rows)

        except Exception as err:
            return xml_format_exception(err)

    def speaker_list_by_id(self, arguments):
        try:
            query_options = {VwDeviceColumns.id: arguments.device_id}
            rows = self.database.speakers_list(query_options)

            return xml_format_speaker_data(rows)

        except Exception as err:
            return xml_format_exception(err)

    def speaker_list_by_uid(self, arguments):
        try:

            query_options = {VwDeviceColumns.uid: arguments.device_uid}

            rows = self.database.speakers_list(query_options)

            return xml_format_speaker_data(rows)

        except Exception as err:
            return xml_format_exception(err)

    def speaker_property_mute(self, arguments):

        try:
            action = arguments.action
            refresh = arguments.refresh
            device_uid = arguments.device_uid

            soco = self.get_soco(device_uid, refresh)

            if soco:
                if action == 0:
                    soco.mute = False
                    return xml_format_status(True, device_uid, '', dict(mute=soco.mute))

                if action == 1:
                    soco.mute = True

                return xml_format_status(True, device_uid, '', dict(mute=soco.mute))

            return xml_format_status(False, device_uid, 'No speaker found with uid \'{}\'. Speaker offline?'.format(device_uid))

        except Exception as err:
            return xml_format_exception(err)

    def speaker_property_statuslight(self, arguments):

        try:
            action = arguments.action
            refresh = arguments.refresh
            device_uid = arguments.device_uid

            soco = self.get_soco(device_uid, refresh)

            if soco:
                if action == 'off':
                    soco.status_light = False
                    return xml_format_status(True, device_uid, '', dict(statuslight=soco.status_light))

                if action == 'on':
                    soco.status_light = True

                return xml_format_status(True, device_uid, '', dict(statuslight=soco.status_light))

            return xml_format_status(False, device_uid, 'No speaker found with uid \'{}\'. Speaker offline?'.format(device_uid))

        except Exception as err:
            return xml_format_exception(err)

    def speaker_property_volume(self, arguments):

        try:
            action = arguments.action
            refresh = arguments.refresh
            device_uid = arguments.device_uid
            device_volume = arguments.device_volume

            soco = self.get_soco(device_uid, refresh)

            if soco:
                if action == 'set':

                    if not device_volume:
                        return xml_format_status(False, device_uid, 'No speaker volume has been set.')

                    soco.volume = device_volume
                    return xml_format_status(True, device_uid, '', dict(volume=soco.volume))

                return xml_format_status(True, device_uid, '', dict(volume=soco.volume))

            return xml_format_status(False, device_uid, 'No speaker found with uid \'{}\'. Speaker offline?'.format(device_uid))

        except Exception as err:
            return xml_format_exception(err)

    def get_soco(self, device_uid, refresh):

        if refresh:
            self.speakers_refresh_quick()

        query_options = {VwDeviceColumns.uid: device_uid}
        speakers = self.database.speakers_list(query_options)

        if speakers:
            return SoCo(speakers[0].ip)

        return None

def check_volume_range(volume):
    value = int(volume)

    if value < 0 or value > 100:
        msg = 'Volume has to be between 0 and 100.'
        raise argparse.ArgumentTypeError(msg)

    return value
