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
import os
from shlex import quote

import inquirer
from inquirer.themes import load_theme_from_dict

from modules.app import banner, helper, logger, traductor
from modules.questioner.questions import question_manager
from modules.system import get_settings
from modules.unix_command import api_json_ouput, command_output, load_json_file


class PyArchboot(object):
    """Application main class.

    When called, it accepts no arguments and returns a new featureless
    instance that has no instance attributes and cannot be given any.

    Arguments:
        object -- base class of the class hierarchy
    """

    def __init__(self):
        """Initialize application settings."""
        self.app = load_json_file('app.json')
        self.packages = load_json_file('packages.json')
        self.theme = load_json_file('theme.json')
        display_banner = banner(self)
        self.logging = logger(self)
        self.args = helper(self)
        self.ipinfo = get_settings().ipinfo()
        self.mirrorlist = get_settings().mirrorlist(
            self.ipinfo['country'].lower())
        lang = self.ipinfo['country'].lower()
        if self.args.lang:
            lang = self.args.lang[0].strip()
        self.trad = traductor(lang)
        self.efi, self.firmware = get_settings().firmware()
        self.drive_list = get_settings().drive(self.trad)
        self.lvm = get_settings().filesystem(self.trad, 'lvm')
        self.luks = get_settings().filesystem(self.trad, 'luks')
        self.ntfs = get_settings().filesystem(self.trad, 'ntfs')
        self.cpu = get_settings().processor()
        self.partition_list = get_settings().partition()
        self.gpu_list = get_settings().vga_controller()

    def run(self):
        """Start the application."""
        if self.args.key:
            cmd = command_output('loadkeys {key}'
                                 .format(key=quote(self.args.key[0].strip())),
                                 exit_on_error=True, timeout=1,
                                 error='invalid keyboard layout !')

        # Ask questions to the user
        self.logging.info(self.trad('use arrow keys to select an option'))
        self.logging.warning(self.trad('all data will be lost !'))
        user = inquirer.prompt(question_manager(self),
                               theme=load_theme_from_dict(self.theme))

        # TESTING
        from pprint import pprint
        pprint(user)


if __name__ == '__main__':
    PyArchboot().run()


# PyArchboot - Python Arch Linux Installer by grm34 under Apache License 2.0
##############################################################################
