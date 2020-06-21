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
import json
import logging
import os
import sys
import time
from shlex import quote

import inquirer
from inquirer.themes import load_theme_from_dict


from modules.app import PyArchboot_help, PyArchboot_logging, app, theme, trad
from modules.settings import get_settings
from modules.unix_command import api_json_ouput, command_output, run_command

from modules.questions import array_of_questions


# Load app settings
with open('{path}/json/app.json'.format(path=os.getcwd()), 'r',
          encoding='utf-8') as app_settings:
    app = json.load(app_settings)

# Load archlinux packages
with open('{path}/json/packages.json'.format(path=os.getcwd()), 'r',
          encoding='utf-8') as packages_list:
    packages = json.load(packages_list)

# Load inquirer theme
with open('{path}/json/theme.json'.format(path=os.getcwd()), 'r',
          encoding='utf-8') as inquirer_theme:
    theme = json.load(inquirer_theme)

# Load app language
language = gettext.translation('PyArchboot', localedir='locales',
                               languages=['{lang}'.format(lang=app['lang'])])
trad = language.gettext

# Get IP address data
    ipinfo = api_json_ouput('https://ipinfo.io?token=26d03faada92e8',
                            exit_on_error=True,
                            error='no internet connection !', timeout=2)

    # Language option (-l, --lang)
    app['lang'] = ipinfo['country'].lower()
    if args.lang:
        app['lang'] = args.lang[0].strip()

    # Keyboard layout option (-k, --key)
    if args.key:
        cmd = command_output('loadkeys {key}'.format(key=quote(args.key)),
                                exit_on_error=True, timeout=1,
                                error='invalid keyboard layout !')


class PyArchboot(object):

    PyArchboot_prepare()

    def __init__(self):

        # Get required system settings
        self.lang = trad
        self.efi, self.firmware = get_settings().firmware()
        self.drive_list = get_settings().drive()
        self.lvm = get_settings().filesystem('lvm')
        self.luks = get_settings().filesystem('luks')
        self.ntfs = get_settings().filesystem('ntfs')
        self.mirrorlist = get_settings().mirrorlist()
        self.cpu = get_settings().processor()
        self.partition_list = get_settings().partition()
        self.gpu_list = get_settings().vga_controller()

        # Ask questions to the user
        logging.info(self.lang('use arrow keys to select an option'))
        logging.warning(self.lang('all data will be lost !'))
        self.user = inquirer.prompt(array_of_questions(self), theme=load_theme_from_dict(theme))
        # while True:
        #     self.user = inquirer.prompt(array_of_questions(self), theme=load_theme_from_dict(theme))
        #     # process_list = [drive_manager(), partition_manager(), vga_manager(),
        #     #                 desktop_manager(), display_manager(),
        #     #                 system_manager(), clean_dictionary()]
        #     # for process in process_list:
        #     #     run = process

        #     logging.warning(trad('this action cannot be canceled !'))

        #     question = [inquirer.Confirm(
        #         'install', message=trad('Do you wish to install Arch Linux now'),
        #         default=True)]

        #     confirm = inquirer.prompt(question, theme=load_theme_from_dict(theme))
        #     if confirm['install'] is False:
        #         break

        # Run module >>> partitioner
        # from modules import partitioner

        # Run module >>> installer
        # from modules import installer
        # logging.info(trad('installation successfull'))

    def reboot(self):
        question = [inquirer.Confirm(
            'reboot', message=trad('Do you wish to reboot your computer now'),
            default=True)]

        confirm = inquirer.prompt(question, theme=load_theme_from_dict(theme))
        if confirm['reboot'] is True:

            # Umount the partitions
            cmd = run_command('umount -f -A -R -q /mnt')

            # Reboot with 5s timeout
            for second in range(5, 0, -1):
                message = 'System will reboot in {second}s'.format(
                    second=str(second))

                cprint(message, 'green', attrs=['bold'], end='\r')
                time.sleep(1)
            cmd = run_command('/usr/bin/reboot')

        else:
            sys.exit(0)


if __name__ == '__main__':
    PyArchboot()


# PyArchboot - Python Arch Linux Installer by grm34 under Apache License 2.0
##############################################################################
