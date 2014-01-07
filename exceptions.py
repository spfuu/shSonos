# -*- coding: utf-8 -*-


class SonosException(Exception):
    """ base exception raised by SoCo, containing the UPnP error code """


class UnknownSonosException(SonosException):
    """ raised if reason of the error can not be extracted

    The exception object will contain the raw response sent back from the
    speaker """


class SonosUPnPException(SonosException):
    """ encapsulates UPnP Fault Codes raised in response to actions sent over
    the network """

    def __init__(self, message, error_code, error_xml, error_description=""):
        self.message = message
        self.error_code = error_code
        self.error_description = error_description
        self.error_xml = error_xml
        
    def __str__(self):
        return self.message
