import json
from abc import ABCMeta, abstractmethod
import logging
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
        instance = class_(obj['parameter'])
        return instance


class JsonCommandBase():
    __metaclass__ = ABCMeta

    def __init__(self, parameter):
        self._status = False
        self._response = ''
        for key, value in parameter.items():
            setattr(self, key, value)

    @abstractmethod
    def run(self):
        raise NotImplementedError("Method 'run' must be implemented!")

    @staticmethod
    def missing_param_error(err):
        s_args = list(filter(None, err.args[0].split("'")))
        return "Missing parameter '{parameter}'!".format(parameter=s_args[-1])


# ## VOLUME #############################################################################################################

class GetVolume(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))

            sonos_speaker.sonos_speakers[self.uid].dirty_property('volume')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
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
            if not utils.check_int(self.volume):
                raise Exception('Value has to be an Integer!')

            volume = int(self.volume)
            if volume not in range(0, 101, 1):
                raise Exception('Volume has to be set between 0 and 100!')

            group_command = False
            if hasattr(self, 'group_command'):
                group_command = self.group_command

            sonos_speaker.sonos_speakers[self.uid].set_volume(volume, trigger_action=True,
                                                              group_command=group_command)
            self._status = True
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
            sonos_speaker.sonos_speakers[self.uid].dirty_property('mute')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
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
            group_command = False
            if hasattr(self, 'group_command'):
                group_command = self.group_command

            sonos_speaker.sonos_speakers[self.uid].set_mute(self.mute, trigger_action=True, group_command=group_command)
            self._status = True
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
            sonos_speaker.sonos_speakers[self.uid].dirty_property('bass')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
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
            if self.bass not in range(-10, 11, 1):
                raise Exception('Bass has to be set between -10 and 10!')

            group_command = False
            if hasattr(self, 'group_command'):
                group_command = self.group_command

            sonos_speaker.sonos_speakers[self.uid].set_bass(self.bass, trigger_action=True, group_command=group_command)
            self._status = True
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
            sonos_speaker.sonos_speakers[self.uid].dirty_property('treble')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
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
            if self.treble not in range(-10, 11, 1):
                raise Exception('Treble has to be set between -10 and 10!')

            group_command = False
            if hasattr(self, 'group_command'):
                group_command = self.group_command
            sonos_speaker.sonos_speakers[self.uid].set_treble(self.treble, trigger_action=True,
                                                              group_command=group_command)
            self._status = True
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
            sonos_speaker.sonos_speakers[self.uid].dirty_property('loudness')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
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
            if self.loudness not in [0, 1, True, False]:
                raise Exception('Loudness has to be 0|1 or True|False !')
            loudness = int(self.loudness)

            group_command = False
            if hasattr(self, 'group_command'):
                group_command = self.group_command
            sonos_speaker.sonos_speakers[self.uid].set_loudness(loudness, trigger_action=True,
                                                                group_command=group_command)
            self._status = True
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
            sonos_speaker.sonos_speakers[self.uid].dirty_property('stop')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
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
            sonos_speaker.sonos_speakers[self.uid].trigger_stop(self.stop)
            self._status = True
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


class GetPlay(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            sonos_speaker.sonos_speakers[self.uid].dirty_property('play')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
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
            sonos_speaker.sonos_speakers[self.uid].trigger_play(self.play)
            self._status = True
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


class GetPause(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            sonos_speaker.sonos_speakers[self.uid].dirty_property('pause')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
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
            sonos_speaker.sonos_speakers[self.uid].trigger_pause(self.pause)
            self._status = True
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


class GetRadioStation(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            sonos_speaker.sonos_speakers[self.uid].dirty_property('radio_station')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


class GetRadioShow(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            sonos_speaker.sonos_speakers[self.uid].dirty_property('radio_show')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
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
            available_playmodes = [
                'normal',
                'shuffle_norepeat',
                'shuffle',
                'repeat_all'
            ]

            if self.playmode.lower() not in available_playmodes:
                raise Exception('Invalid Playmode \'{mode}\'. Available modes : normal, shuffle, shuffle_norepeat, '
                                'repeat_all'.format(mode=self.playmode))

            sonos_speaker.sonos_speakers[self.uid].trigger_playmode(self.playmode)
            self._status = True
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


class GetPlaymode(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            sonos_speaker.sonos_speakers[self.uid].dirty_property('playmode')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response


class GetAlarms(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            logger.debug('COMMAND {classname} -- attributes: {attributes}'.format(classname=self.__class__.__name__,
                                                                                  attributes=utils.dump_attributes(
                                                                                      self)))
            sonos_speaker.sonos_speakers[self.uid].get_alarms()
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True

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
            sonos_speaker.sonos_speakers[self.uid].dirty_property('track_artist')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
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
            sonos_speaker.sonos_speakers[self.uid].dirty_property('track_title')
            sonos_speaker.sonos_speakers[self.uid].send()
            self._status = True
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
            if self.led not in [0, 1, True, False]:
                raise Exception('Led has to be 0|1 or True|False !')

            led = int(self.led)

            group_command = False
            if hasattr(self, 'group_command'):
                group_command = self.group_command

            sonos_speaker.sonos_speakers[self.uid].set_led(led, trigger_action=True,
                                                           group_command=group_command)
            self._status = True
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
            sonos_speaker.sonos_speakers[self.uid].dirty_property('led')
            self._status = True
        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            self._response = err
        finally:
            return self._status, self._response