from __future__ import unicode_literals

# -*- coding: utf-8 -*-
import base64
import ctypes
import json
import os
import platform
import requests
import re
import urllib
import urllib.request

try:
    from types import StringType, UnicodeType

except ImportError:
    StringType = bytes
    UnicodeType = str


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
        return int(round(free_bytes.value/1024/1024, 0))
    else:
        st = os.statvfs(folder)
        return int(round(st.f_bavail * st.f_frsize/1024/1024, 0))

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
        #since this is a const value, no more files will be written (only this mp3 onetime)
        tts_language = 'en'
        tts_string ='Cannot save file. File size quota exceeded!'

    url = "http://translate.google.com/translate_tts?ie=UTF-8&tl={tts_language}&q={tts_string}"
    url = url.format(tts_language=tts_language, tts_string=urllib.request.quote(tts_string))
    base64_name = base64.b64encode('{}__{}'.format(tts_language, tts_string).encode('utf-8')).decode('ascii')

    fname = '{}.mp3'.format(base64_name)
    abs_fname = os.path.join(local_share, fname)

    #check if file exists, no need to browse google tts
    if os.path.exists(abs_fname):
        return fname

    try:
        response = requests.get(url)
        if response and response.status_code == 200:
            with open(abs_fname, 'wb') as file:
                file.write(response.content)
            return fname
        else:
            raise requests.RequestException('Status code: {}'.format(response.status_code))
    except requests.RequestException as e:
        raise("Couldn't obtain TTS from Google.\nError: {}".format(e.errno))

def to_JSON(value):
        return json.dumps(value, default=lambda o: value, ensure_ascii=False)

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
