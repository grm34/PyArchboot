# -*- coding: utf-8 -*-

"""Copyright 2020 Jeremy Pardo @grm34 https://github.com/grm34.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import argparse
import gettext
from shlex import quote

from termcolor import colored, cprint

from .system_manager.unix_command import command_output


def app_banner(self):
    """Display ASCII banner of the application.

    Modules
    -------
        termcolor: "ANSII Color formatting for output in terminal"

    Returns
    -------
        "Title with a short description of the application"
    """
    for key in range(4):
        cprint(self.app['ascii{key}'.format(key=key)], 'blue', attrs=['bold'])

    cprint(self.app['title'], 'red', attrs=['bold'])

    for key in range(7):
        cprint(self.app['description{key}'.format(key=key)], 'white')

    cprint(self.app['separator'], 'blue', attrs=['bold'])


def app_helper(self):
    """Application usage and command line options.

    Modules
    -------
        argparse: "Argument handler for parsing command line strings"
        termcolor: "ANSII Color formatting for output in terminal"
        shlex.quote: "Return a shell-escaped version of the string"

    Submodules
    ----------
        `command_output`: "Subprocess `check_output` with return codes"

    Options
    -------
        help: "Display usage and exit"
        ntp: "Update the system clock with NTP"
        time: "Update the system clock manually"
        lang: "Installer language selection"
        keyboard: "Keyboard layout selection"
        file: "Install additional packages from file"
        theme: "Application theme selection"

    Returns
    -------
        options: "Tuple containing command line options from sys.argv"
    """
    parser = argparse.ArgumentParser(
        prog=colored(self.app['name'], 'green', attrs=['bold']),
        description=colored(self.app['title'], 'white', attrs=['bold']),
        usage=colored(self.app['usage'], 'grey', 'on_cyan'),
        epilog=colored(
            'More information at {url}'
            .format(url=colored(self.app['url'], 'cyan', attrs=['bold'])),
            'white', attrs=['bold']))

    group = parser.add_mutually_exclusive_group()

    group.add_argument('--ntp',
                       action='store_true',
                       help='Update the system clock with NTP')

    group.add_argument('--time',
                       nargs=1,
                       metavar='{HH:MM:SS}',
                       help='Update the system clock manually')

    parser.add_argument('--lang',
                        nargs=1,
                        choices=['de', 'en', 'es', 'fr', 'ru'],
                        help='Installer language selection')

    parser.add_argument('--keyboard',
                        nargs=1,
                        metavar='{keymap,lang,...}',
                        help='Keyboard layout selection')

    parser.add_argument('--file',
                        nargs=1,
                        metavar='{file,list,...}',
                        help='Install additional packages from file')

    parser.add_argument('--theme',
                        nargs=1,
                        choices=['default', 'bacon', 'matrix'],
                        help='Application theme selection')

    options = parser.parse_args()
    if options.keyboard:
        cmd = command_output('loadkeys {key}'
                             .format(key=quote(options.keyboard[0].strip())),
                             exit_on_error=True,
                             timeout=1,
                             error='invalid keyboard layout !')

    if options.ntp:
        ntp_system_clock = command_output(
            '/usr/bin/timedatectl set-ntp true', timeout=1)

    if options.time:
        manual_system_clock = command_output(
            '/usr/bin/timedatectl set-time {time}'
            .format(time=quote(options.time[0].strip())),
            timeout=1)

    return options


def app_translator(lang):
    """Localization of the application.

    Arguments
    ---------
        lang: "String containing application language"

    Modules
    -------
        gettext: "Internationalization and localization support"

    Returns
    -------
        trad: "Function to translate string"
    """
    language = gettext.translation('PyArchboot',
                                   localedir='locales',
                                   languages=['{lang}'.format(lang=lang)])
    trad = language.gettext
    return trad


# PyArchboot - Python Arch Linux Installer by grm34 under Apache License 2.0
##############################################################################
