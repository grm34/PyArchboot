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
import logging
import os

import coloredlogs
from termcolor import colored, cprint

from .unix_command import command_output


def banner(self):
    """Display ASCII banner of the application.

    Modules:
        termcolor -- ANSII Color formatting for output in terminal

    Returns:
        print elements -- Title with a short description of the application
    """
    for key in range(4):
        cprint(self.app['ascii{key}'.format(key=key)], 'blue', attrs=['bold'])

    cprint(self.app['title'], 'red', attrs=['bold'])

    for key in range(7):
        cprint(self.app['description{key}'.format(key=key)], 'white')

    cprint(self.app['separator'], 'blue', attrs=['bold'])


def logger(self):
    """Logging handler wich can be used in modules.

    Writes to logs/PyArchboot.log and display output to terminal.

    Modules:
        os -- Export all functions from posix
        logging -- Event logging system for applications and libraries,
        coloredlogs -- Colored terminal output

    SubModules:
        command_output -- Get the output of a shell command

    Requirements:
        Update the system clock before creating the logger

    Returns:
        logging -- application object logger
    """
    set_time = command_output('/usr/bin/timedatectl set-ntp true', timeout=1)

    # Create a StreamHandler wich write to sys.stderr
    pre = '%(asctime)s [%(levelname)s] %(pathname)s:%(lineno)d [%(funcName)s]'
    message = '{level} %(message)s'.format(level=pre)
    logging.basicConfig(filename='{path}/logs/{appname}.log'.format(
                        path=os.getcwd(), appname=self.app['name']),
                        level=logging.DEBUG, filemode='w', format=message)

    # Create a logger for terminal output
    console = logging.getLogger()

    # Set colored terminal output
    coloredlogs.install(
        level='INFO', logger=console, datefmt='%H:%M:%S',
        fmt='[%(asctime)s] %(levelname)s > %(message)s',
        level_styles={'critical': {'bold': True, 'color': 'red'},
                      'debug': {'color': 'green'},
                      'error': {'color': 'red'},
                      'info': {'color': 'cyan'},
                      'warning': {'color': 'yellow', 'bold': True}},
        field_styles={'levelname': {'bold': True, 'color': 'green'},
                      'asctime': {'color': 'yellow'}})

    # Return handler wich can be used in modules
    return logging


def helper(self):
    """Argument handler for parsing command line strings.

    Modules:
        argparse -- Optparse-inspired command-line parsing library,
        termcolor -- ANSII Color formatting for output in terminal

    Options:
        -h, --help -- Display usage and exit,
        -l, --lang -- Installer language selection,
        -k, --key  -- Keyboard layout selection,
        -f, --file -- Install additional packages from file

    Returns:
        args {tuple} -- command line options from sys.argv
    """
    parser = argparse.ArgumentParser(
        prog=colored(self.app['name'], 'green', attrs=['bold']),
        description=colored(self.app['title'], 'white', attrs=['bold']),
        usage=colored(self.app['usage'], 'grey', 'on_cyan'),
        epilog=colored('More information at {url}'
                       .format(url=colored(self.app['url'],
                                           'cyan', attrs=['bold']))))

    parser.add_argument('-l', '--lang', nargs=1,
                        choices=['de', 'en', 'es', 'fr', 'ru'],
                        help='Installer language selection')

    parser.add_argument('-k', '--key', nargs=1,
                        help='Keyboard layout selection')

    # parser.add_argument('-f', '--file', nargs=1,
    #                     help='Install additional packages from file')

    args = parser.parse_args()
    return args


def traductor(lang):
    """Interface to the GNU gettext message catalog library.

    Arguments:
        lang -- String containing application language

    Modules:
        gettext -- Internationalization and localization support

    Returns:
        trad -- Function to translate string
    """
    language = gettext.translation('PyArchboot', localedir='locales',
                                   languages=['{lang}'.format(lang=lang)])
    trad = language.gettext
    return trad


# PyArchboot - Python Arch Linux Installer by grm34 under Apache License 2.0
##############################################################################
