import json
from abc import ABCMeta, abstractmethod
from lib_sonos import sonos_speaker
from lib_sonos.utils import underscore_to_camel
from soco import alarms


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


class GetAlarms(JsonCommandBase):
    def __init__(self, parameter):
        super().__init__(parameter)

    def run(self):
        try:
            sonos_speaker.sonos_speakers[self.uid].get_alarms()
            self._status = True


        except AttributeError as err:
            self._response = JsonCommandBase.missing_param_error(err)
        except Exception as err:
            print(err)
        finally:
            return self._status, self._response