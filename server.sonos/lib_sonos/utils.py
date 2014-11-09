from __future__ import unicode_literals

# -*- coding: utf-8 -*-
import base64
import ctypes
import json
import os
import platform
import socket
import requests
import re
import urllib
import urllib.request
import logging
import sys

if os.name != "nt":
    import fcntl
    import struct

try:
    from types import StringType, UnicodeType

except ImportError:
    StringType = bytes
    UnicodeType = str

logger = logging.getLogger('')


def really_unicode(in_string):
    """
    Ensures s is returned as a unicode string and not just a string through
    a series of progressively relaxed decodings

    """
    if type(in_string) is StringType:
        for args in (('utf-8',), ('latin-1',), ('ascii', 'replace')):
            try:
                in_string = in_string.decode(*args)
                break
            except UnicodeDecodeError:
                continue
    if type(in_string) is not UnicodeType:
        raise ValueError('%s is not a string at all.' % in_string)
    return in_string


def really_utf8(in_string):
    """ First decodes s via really_unicode to ensure it can successfully be
    encoded as utf-8 This is required since just calling encode on a string
    will often cause python to perform a coerced strict auto-decode as ascii
    first and will result in a UnicodeDecodeError being raised After
    really_unicode returns a safe unicode string, encode as 'utf-8' and return
    the utf-8 encoded string.

    """
    return really_unicode(in_string).encode('utf-8')


def camel_to_underscore(string):
    """ Convert camelcase to lowercase and underscore
    Recipy from http://stackoverflow.com/a/1176023
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def underscore_to_camel(value):
    return ''.join(x.capitalize() or '_' for x in value.split('_'))


def prettify(unicode_text):
    """Return a pretty-printed version of a unicode XML string. Useful for
    debugging.

    """
    import xml.dom.minidom

    reparsed = xml.dom.minidom.parseString(unicode_text.encode('utf-8'))
    return reparsed.toprettyxml(indent="  ", newl="\n")


def get_free_space_mb(folder):
    """ Return folder/drive free space (in bytes)
    """
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        return int(round(free_bytes.value / 1024 / 1024, 0))
    else:
        st = os.statvfs(folder)
        return int(round(st.f_bavail * st.f_frsize / 1024 / 1024, 0))


def check_directory_permissions(local_share):
    if not os.path.exists(local_share):
        print('Local share \'{}\' does not exists!'.format(local_share))
        return False

    return os.access(local_share, os.W_OK) and os.access(local_share, os.R_OK)


def get_folder_size(folder):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def save_google_tts(local_share, tts_string, tts_language, quota):
    size = int(get_folder_size(local_share) / 1024 / 1024)
    if size == 0:
        size = 1

    if quota < size:
        # since this is a const value, no more files will be written (only this mp3 onetime)
        tts_language = 'en'
        tts_string = 'Cannot save file. File size quota exceeded!'

    url = "http://translate.google.com/translate_tts?ie=UTF-8&tl={tts_language}&q={tts_string}"
    url = url.format(tts_language=tts_language, tts_string=urllib.request.quote(tts_string))
    base64_name = base64.urlsafe_b64encode('{}__{}'.format(tts_language, tts_string).encode('utf-8')).decode('ascii', '')

    fname = '{}.mp3'.format(base64_name)
    abs_fname = os.path.join(local_share, fname)

    # check if file exists, no need to browse google tts
    if os.path.exists(abs_fname):
        return fname

    try:
        response = requests.get(url)
        if response and response.status_code == 200:
            with open(abs_fname, 'wb') as file:
                file.write(response.content)
            os.chmod(abs_fname, 0o444)
            return fname
        else:
            raise requests.RequestException('Status code: {}'.format(response.status_code))
    except requests.RequestException as e:
        raise ("Couldn't obtain TTS from Google.\nError: {}".format(e.errno))


def to_json(value):
    return json.dumps(value, default=lambda o: value, ensure_ascii=False, indent=4)


def check_volume_range(volume):
    if volume < 0 or volume > 100:
        print('Volume has to be between 0 and 100.')
        return False
    return True


def url_fix(s, charset='utf-8'):
    """Sometimes you get an URL by a user that just isn't a real
    URL because it contains unsafe characters like ' ' and so on.  This
    function can fix some of the problems in a similar way browsers
    handle data entered by the user:

    'http://de.wikipedia.org/wiki/Elf%20%28Begriffskl%C3%A4rung%29'

    :param charset: The target charset for the URL if the url was
                    given as unicode string.
    """
    if isinstance(s, str):
        s = s.encode(charset, 'ignore')
    scheme, netloc, path, query, fragment = urllib.parse.urlsplit(s)
    path = urllib.parse.quote(path, '/%').encode(charset)
    query = urllib.parse.quote_plus(query, ':&=').encode(charset)
    return urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))


def check_max_volume_exceeded(volume, max_volume):
    volume = int(volume)
    if max_volume > -1:
        if volume > max_volume:
            return True
    return False


def check_bass_range(value):
    if value < -10 or value > 10:
        return False
    return True


def check_treble_range(value):
    if value < -10 or value > 10:
        return False
    return True


def debug_log_commands(ip, arguments):
    logger.debug("arguments: {arguments} | ip: {ip}".format(arguments=', '.join(arguments), ip=ip))


def get_interface_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15].encode('utf-8')))[20:24])


def dump_attributes(obj):
    attrs = vars(obj)
    attributes = ', '.join("%s: %s" % item for item in attrs.items() if not item[0].startswith('_'))
    return attributes

def ip_address_is_valid(address):

    """
    Tests if an ip address is valid.
    http://stackoverflow.com/questions/4011855/regexp-to-check-if-an-ip-is-valid
    :param address:
    :return: True or False
    """

    try:
        socket.inet_aton(address)
    except socket.error:
        return False
    else:
        return address.count('.') == 3

def check_int(s):
    if isinstance(s, int):
        return True
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()


def get_lan_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = ["eth0", "eth1", "eth2", "wlan0", "wlan1", "wifi0", "ath0", "ath1", "ppp0"]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break
            except IOError:
                pass
    return ip

# #######################################################################################################################
'''
Notification list from http://stackoverflow.com/questions/13259179/list-callbacks
'''

def callback_method(func):
    def notify(self, *args, **kwargs):
        for _, callback in self._callbacks:
            callback()
        return func(self, *args, **kwargs)

    return notify


_pyversion = sys.version_info[0]


class NotifyList(list):
    extend = callback_method(list.extend)
    append = callback_method(list.append)
    remove = callback_method(list.remove)
    pop = callback_method(list.pop)
    __delitem__ = callback_method(list.__delitem__)
    __setitem__ = callback_method(list.__setitem__)
    __iadd__ = callback_method(list.__iadd__)
    #__imul__ = callback_method(list.__imul__)

    #Take care to return a new NotifyList if we slice it.
    if _pyversion < 3:
        __setslice__ = callback_method(list.__setslice__)
        __delslice__ = callback_method(list.__delslice__)

        def __getslice__(self, *args):
            return self.__class__(list.__getslice__(self, *args))

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.__class__(list.__getitem__(self, item))
        else:
            return list.__getitem__(self, item)

    def __init__(self, *args):
        list.__init__(self, *args)
        self._callbacks = []
        self._callback_cntr = 0

    def register_callback(self, cb):
        self._callbacks.append((self._callback_cntr, cb))
        self._callback_cntr += 1
        return self._callback_cntr - 1

    def unregister_callback(self, cbid):
        for idx, (i, cb) in enumerate(self._callbacks):
            if i == cbid:
                self._callbacks.pop(idx)
                return cb
        else:
            return None