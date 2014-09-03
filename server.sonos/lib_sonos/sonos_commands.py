import json
from abc import ABCMeta, abstractmethod
import logging
import re
from lib_sonos.sonos_library import SonosLibrary
from lib_sonos.definitions import TIMESTAMP_PATTERN, SCAN_TIMEOUT
from lib_sonos.udp_broker import UdpBroker
from soco.exceptions import SoCoUPnPException
from lib_sonos import sonos_speaker
from lib_sonos import utils
from lib_sonos.utils import underscore_to_camel

logger = logging.getLogger('')


class MyDecoder(json.JSONDecoder):
    def decode(self, json_string):
        obj = json.loads(json_string)
        module = __import__(__name__, fromlist=['sonos.json_commands'])

        '''
         class name must be camel case, convert it
        '''
        class_name = underscore_to_camel(obj['command'])
        class_ = getattr(module, class_name)

        if 'parameter' in obj:
            instance = class_(obj['parameter'])
        else:
            instance = class_(obj)
        return instance


class JsonCommandBase():
    __metaclass__ = ABCMeta

    def __init__(self, parameter=None):
        self._status = False
        self._response = ''

        if parameter is not None:
            for key, value in parameter.items():
                setattr(self, key, value)

    @abstractmethod
    def run(self):
        raise NotImplementedError("Method 'run' must be implemented!")

    @staticmethod
    def missing_param_error(err):
        s_args = list(filter(None, err.args[0].split("'")))
        return "Missing parameter '{parameter}'!".format(parameter=s_args[-1])


### CLIENT SUBSCRIBE / UNSUBSCRIE ######################################################################################

class ClientSubscribe(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if not utils.check_int(self.port):
                raise Exception('Port \'{port}\' is not an Integer!'.format(port=self.port))
            port = int(self.port)

            if port not in range(1, 65536, 1):
                raise Exception('Port \'{port}\' is not in range [1-65535].'.format(port=port))

            if not utils.ip_address_is_valid(self.ip):
                raise Exception('IP address \'{ip}\' is not valid.'.format(ip=self.ip))

            UdpBroker.subscribe_client(self.ip, self.port)
            self._status = True
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


class ClientUnsubscribe(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if not utils.check_int(self.port):
                raise Exception('Port \'{port}\' is not an Integer!'.format(port=self.port))
            port = int(self.port)

            if port not in range(1, 65536, 1):
                raise Exception('Port \'{port}\' is not in range [1-65535].'.format(port=port))

            if not utils.ip_address_is_valid(self.ip):
                raise Exception('IP address \'{ip}\' is not valid.'.format(ip=self.ip))

            UdpBroker.unsubscribe_client(self.ip, port)
            self._status = True
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### CURRENT STATE ######################################################################################################

class CurrentState(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))
            self._status = True

            group_command = 0
            if hasattr(self, 'group_command'):
                if self.group_command not in [0, 1, True, False, '0', '1']:
                    raise Exception('The parameter \'group_command\' has to be 0|1 or True|False !')
                group_command = int(self.group_command)

            sonos_speaker.sonos_speakers[self.uid].current_state(group_command)
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True

        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### VOLUME #############################################################################################################

class GetVolume(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].dirty_property('volume')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


class SetVolume(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            if not utils.check_int(self.volume):
                raise Exception('Value has to be an Integer!')

            volume = int(self.volume)
            if volume not in range(0, 101, 1):
                raise Exception('Volume has to be set between 0 and 100!')

            group_command = 0
            if hasattr(self, 'group_command'):
                if self.group_command not in [0, 1, True, False, '0', '1']:
                    raise Exception('The parameter \'group_command\' has to be 0|1 or True|False !')
                group_command = int(self.group_command)

            sonos_speaker.sonos_speakers[self.uid].set_volume(volume, trigger_action=True,
                                                              group_command=group_command)
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


# ## VOLUME UP ##########################################################################################################

class VolumeUp(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            group_command = 0
            if hasattr(self, 'group_command'):
                if self.group_command not in [0, 1, True, False, '0', '1']:
                    raise Exception('The parameter \'group_command\' has to be 0|1 or True|False !')
                group_command = int(self.group_command)

            sonos_speaker.sonos_speakers[self.uid].volume_up(group_command=group_command)
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### VOLUME DOWN ########################################################################################################

class VolumeDown(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            group_command = 0
            if hasattr(self, 'group_command'):
                if self.group_command not in [0, 1, True, False, '0', '1']:
                    raise Exception('The parameter \'group_command\' has to be 0|1 or True|False !')
                group_command = int(self.group_command)

            sonos_speaker.sonos_speakers[self.uid].volume_down(group_command=group_command)
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### MAX VOLUME #########################################################################################################

class GetMaxVolume(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].dirty_property('max_volume')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


class SetMaxVolume(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            if not utils.check_int(self.maxvolume):
                raise Exception('Value has to be an Integer!')
            maxvolume = int(self.maxvolume)

            if maxvolume not in range(-1, 101, 1):
                raise Exception('MaxVolume has to be set between 0 and 100!')
            group_command = False

            group_command = 0
            if hasattr(self, 'group_command'):
                if self.group_command not in [0, 1, True, False, '0', '1']:
                    raise Exception('The parameter \'group_command\' has to be 0|1 or True|False !')
                group_command = int(self.group_command)

            sonos_speaker.sonos_speakers[self.uid].set_maxvolume(maxvolume, group_command=group_command)

            '''
            max_volume is not triggered by sonos events, do it manually
            '''
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### MUTE ###############################################################################################################

class GetMute(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].dirty_property('mute')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


class SetMute(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            group_command = 0
            if hasattr(self, 'group_command'):
                if self.group_command not in [0, 1, True, False, '0', '1']:
                    raise Exception('The parameter \'group_command\' has to be 0|1 or True|False !')
                group_command = int(self.group_command)

            sonos_speaker.sonos_speakers[self.uid].set_mute(self.mute, trigger_action=True, group_command=group_command)
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### BASS ###############################################################################################################

class GetBass(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].dirty_property('bass')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


class SetBass(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            if self.bass not in range(-10, 11, 1):
                raise Exception('Bass has to be set between -10 and 10!')

            group_command = 0
            if hasattr(self, 'group_command'):
                if self.group_command not in [0, 1, True, False, '0', '1']:
                    raise Exception('The parameter \'group_command\' has to be 0|1 or True|False !')
                group_command = int(self.group_command)

            sonos_speaker.sonos_speakers[self.uid].set_bass(self.bass, trigger_action=True, group_command=group_command)
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### TREBLE #############################################################################################################

class GetTreble(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].dirty_property('treble')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


class SetTreble(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            if self.treble not in range(-10, 11, 1):
                raise Exception('Treble has to be set between -10 and 10!')

            group_command = 0
            if hasattr(self, 'group_command'):
                if self.group_command not in [0, 1, True, False, '0', '1']:
                    raise Exception('The parameter \'group_command\' has to be 0|1 or True|False !')
                group_command = int(self.group_command)

            sonos_speaker.sonos_speakers[self.uid].set_treble(self.treble, trigger_action=True,
                                                              group_command=group_command)
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### LOUDNESS ###########################################################################################################

class GetLoudness(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].dirty_property('loudness')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


class SetLoudness(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            if self.loudness not in [0, 1, True, False, '0', '1']:
                raise Exception('Loudness has to be 0|1 or True|False !')
            loudness = int(self.loudness)

            group_command = 0
            if hasattr(self, 'group_command'):
                if self.group_command not in [0, 1, True, False, '0', '1']:
                    raise Exception('The parameter \'group_command\' has to be 0|1 or True|False !')
                group_command = int(self.group_command)

            sonos_speaker.sonos_speakers[self.uid].set_loudness(loudness, trigger_action=True,
                                                                group_command=group_command)
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### STOP ###############################################################################################################

class GetStop(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].dirty_property('stop')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


class SetStop(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].set_stop(self.stop, trigger_action=True)
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### PLAY ###############################################################################################################

class GetPlay(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].dirty_property('play')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


class SetPlay(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].set_play(self.play, trigger_action=True)
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### PAUSE ##############################################################################################################

class GetPause(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].dirty_property('pause')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


class SetPause(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].set_pause(self.pause, trigger_action=True)
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### RADIO STATION ######################################################################################################

class GetRadioStation(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].dirty_property('radio_station')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### RADIO SHOW #########################################################################################################

class GetRadioShow(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].dirty_property('radio_show')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### PLAYMODE ###########################################################################################################

class GetPlaymode(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].dirty_property('playmode')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


class SetPlaymode(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            available_playmodes = [
                'normal',
                'shuffle_norepeat',
                'shuffle',
                'repeat_all'
            ]

            if self.playmode.lower() not in available_playmodes:
                raise Exception('Invalid Playmode \'{mode}\'. Available modes : normal, shuffle, shuffle_norepeat, '
                                'repeat_all'.format(mode=self.playmode))

            sonos_speaker.sonos_speakers[self.uid].set_playmode(self.playmode, trigger_action=True)
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### ALARMS #############################################################################################################

class GetAlarms(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].get_alarms()
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### TRACK ARTIST #######################################################################################################

class GetTrackArtist(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].dirty_property('track_artist')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### TRACK TITLE ########################################################################################################

class GetTrackTitle(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].dirty_property('track_title')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### LED ################################################################################################################

class SetLed(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            if self.led not in [0, 1, True, False, '1', '0']:
                raise Exception('Led has to be 0|1 or True|False !')

            led = int(self.led)

            group_command = 0
            if hasattr(self, 'group_command'):
                if self.group_command not in [0, 1, True, False, '0', '1']:
                    raise Exception('The parameter \'group_command\' has to be 0|1 or True|False !')
                group_command = int(self.group_command)

            sonos_speaker.sonos_speakers[self.uid].set_led(led, trigger_action=True,
                                                           group_command=group_command)
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


class GetLed(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].dirty_property('led')
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### NEXT ###############################################################################################################

class Next(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            try:
                sonos_speaker.sonos_speakers[self.uid].next()
                self._status = True
            except SoCoUPnPException as err:
                '''
                illegal seek action, no more items in playlist, uncritical
                '''
                if err.error_code != '711':
                    raise err
                self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### PREVIOUS ###########################################################################################################

class Previous(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            try:
                sonos_speaker.sonos_speakers[self.uid].previous()
                self._status = True
            except SoCoUPnPException as err:
                '''
                illegal seek action, no more items in playlist, uncritical
                '''
                if err.error_code != '711':
                    raise err
                self._status = True

        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### TRACK POSITION #####################################################################################################

class GetTrackPosition(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            force_refresh = 0
            if hasattr(self, 'force_refresh'):
                if self.force_refresh not in [0, 1, True, False, '0', '1']:
                    raise Exception('Led has to be 0|1 or True|False !')
                force_refresh = int(self.force_refresh)

            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            if force_refresh:
                sonos_speaker.sonos_speakers[self.uid].get_trackposition(force_refresh=True)
            else:
                sonos_speaker.sonos_speakers[self.uid].dirty_property('track_position')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True

        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


class SetTrackPosition(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            if not re.match(TIMESTAMP_PATTERN, self.timestamp):
                raise Exception(
                    '\'{timestamp}\' is ot a valid timestamp. Use HH:MM:ss !'.format(timestamp=self.timestamp))

            sonos_speaker.sonos_speakers[self.uid].set_trackposition(self.timestamp, trigger_action=True)
            self._status = True

        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### PARTYMODE ##########################################################################################################

class Partymode(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].partymode()
            self._status = True

        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### JOIN ###############################################################################################################

class Join(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].join(self.join_uid)
            self._status = True

        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### UNJOIN #############################################################################################################

class Unjoin(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].unjoin()
            self._status = True

        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### CLIENT LIST ########################################################################################################

class ClientList(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            data = ''
            for uid, speaker in sonos_speaker.sonos_speakers.items():
                data += "<p>uid: {}</p>".format(speaker.uid)
                data += "<p>ip: {}</p>".format(speaker.ip)
                data += "<p>model: {}</p>".format(speaker.model)
                data += "<p>current zone: {}</p>".format(speaker.zone_name)
                data += "<p>----------------------</p>"

                logger.debug("active speakers: {uid} | {ip} | {model} | {zone}".
                             format(uid=speaker.uid, ip=speaker.ip, model=speaker.model, zone=speaker.zone_name))
            if not data:
                logger.debug('no speakers online')
                data = "No speakers online! Discover scan is performed every {} seconds.".format(SCAN_TIMEOUT)

            self._response = data
            self._status = True

        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### PLAY URI ###########################################################################################################

class PlayUri(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            sonos_speaker.sonos_speakers[self.uid].play_uri(self.uri)
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response

### PLAY SNIPPET #######################################################################################################

class PlaySnippet(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            group_command = 0
            if hasattr(self, 'group_command'):
                if self.group_command not in [0, 1, True, False, '0', '1']:
                    raise Exception('The parameter \'group_command\' has to be 0|1 or True|False !')
                group_command = int(self.group_command)

            volume = -1
            if hasattr(self, 'volume'):
                if not utils.check_int(self.volume):
                    raise Exception('Value has to be an Integer!')
                volume = int(self.volume)
                if volume not in range(-1, 101, 1):
                    raise Exception('Volume has to be set between -1 and 100!')

            sonos_speaker.sonos_speakers[self.uid].play_snippet(self.uri, volume, group_command=group_command)
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


### PLAY TTS ###########################################################################################################

class PlayTts(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            if self.uid not in sonos_speaker.sonos_speakers:
                raise Exception('No speaker found with uid \'{uid}\'!'.format(uid=self.uid))

            if len(self.tts) > 100:
                raise Exception('Text-to-Speech string must not be greater than 100 characters.')

            group_command = 0
            if hasattr(self, 'group_command'):
                if self.group_command not in [0, 1, True, False, '0', '1']:
                    raise Exception('The parameter \'group_command\' has to be 0|1 or True|False !')
                group_command = int(self.group_command)

            volume = -1
            if hasattr(self, 'volume'):
                if not utils.check_int(self.volume):
                    raise Exception('Value has to be an Integer!')
                volume = int(self.volume)
                if volume not in range(-1, 101, 1):
                    raise Exception('Volume has to be set between -1 and 100!')

            language = 'en'
            if hasattr(self, 'language'):
                language = self.language

            sonos_speaker.sonos_speakers[self.uid].play_tts(self.tts, volume, language, group_command=group_command)
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response







### GET FAVORITE RADIO STATIONS ########################################################################################

class GetFavoriteRadioStations(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            start_item = 0
            if hasattr(self, 'start_item'):
                if not utils.check_int(self.start_item):
                    raise Exception('The parameter \'start_item\' has to be an integer!')
                start_item = int(self.start_item)

            max_items = 50
            if hasattr(self, 'max_items'):
                if not utils.check_int(self.start_item):
                    raise Exception('The parameter \'max_items\' has to be an integer!')
                max_items = int(self.max_items)

            self._response = SonosLibrary.get_fav_radiostations(start_item, max_items)
            self._status = True
        except ConnectionError:
            self._response = 'Unable to process command. Speaker with uid \'{uid}\'seems to be offline.'.\
                format(uid=self.uid)
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response
