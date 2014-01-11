# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import argparse
import sys

""" Provides general utility functions to be used across modules """

import re

try:
    from types import StringType, UnicodeType

except ImportError:
    StringType = bytes
    UnicodeType = str


class ArgumentParser(argparse.ArgumentParser):
    def _get_action_from_name(self, name):
        """Given a name, get the Action instance registered with this parser.
        If only it were made available in the ArgumentError object. It is
        passed as it's first arg...
        """
        container = self._actions
        if name is None:
            return None
        for action in container:
            if '/'.join(action.option_strings) == name:
                return action
            elif action.metavar == name:
                return action
            elif action.dest == name:
                return action

    def error(self, message):
        usage = self.format_usage()
        raise Exception('%s%s' % (usage, message))

    def exit(self, status=0, message=None):
        sys.exit(self.format_help())

    def get_argparse_help_recursively(self, actions, help_dictionary):

        subparsers_actions = [action for action in actions if isinstance(action, argparse._SubParsersAction)]

        for subparsers_action in subparsers_actions:
        # get all subparsers and print help
            for choice, subparser in subparsers_action.choices.items():
                help_dictionary[choice] = subparser.format_help()
                if subparser._actions:
                    self.get_argparse_help_recursively(subparser._actions, help_dictionary)

    def get_help_from_subparser_option(self, args):

        help_dictionary = {}
        self.get_argparse_help_recursively(self._actions, help_dictionary)

        if args:

            error_suboption = ''

            # find key with None-Value, this is the option, where the argparse error has occurred
            for k, v in vars(args).items():
                if not v:
                    error_suboption = k
                    break

            if error_suboption and help_dictionary[error_suboption]:
                return help_dictionary[error_suboption]

            #if not found, print the entire help

            help = ''
            for k, v in help_dictionary.items():
                help += v
            return help


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

