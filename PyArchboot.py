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
import logging
import os

import coloredlogs
import inquirer
from inquirer.themes import load_theme_from_dict

from modules.app import app_banner, app_helper, app_translator
from modules.questioner.questions import question_manager
from modules.system import GetSettings
from modules.unix_command import load_json_file

# Create a StreamHandler wich write to sys.stderr
level = '%(asctime)s [%(levelname)s] %(pathname)s:%(lineno)d [%(funcName)s]'
message = '{level} %(message)s'.format(level=level)
logging.basicConfig(filename='{path}/logs/{appname}.log'
                    .format(path=os.getcwd(), appname='PyArchboot'),
                    level=logging.DEBUG,
                    filemode='w',
                    format=message)

# Create a logger for terminal output
console = logging.getLogger()
coloredlogs.install(
    level='INFO',
    logger=console,
    datefmt='%H:%M:%S',
    fmt='[%(asctime)s] %(levelname)s > %(message)s',
    level_styles={'critical': {'bold': True, 'color': 'red'},
                  'debug': {'color': 'green'},
                  'error': {'color': 'red'},
                  'info': {'color': 'cyan'},
                  'warning': {'color': 'yellow', 'bold': True}},
    field_styles={'levelname': {'bold': True, 'color': 'green'},
                  'asctime': {'color': 'yellow'}})


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
        self.display_banner = app_banner(self)
        self.options = app_helper(self)
        self.packages = load_json_file('packages.json')
        self.theme = load_json_file('theme.json')
        self.ipinfo = GetSettings()._ipinfo()
        self.mirrorlist = GetSettings()._mirrorlist(
            self.ipinfo['country'].lower())
        self.language = self.ipinfo['country'].lower()
        if self.options.lang:
            self.language = self.options.lang[0].strip()
        self.trad = app_translator(self.language)
        self.efi, self.firmware = GetSettings()._firmware()
        self.drive_list = GetSettings()._drive(self.trad)
        self.lvm = GetSettings()._filesystem(self.trad, 'lvm')
        self.luks = GetSettings()._filesystem(self.trad, 'luks')
        self.ntfs = GetSettings()._filesystem(self.trad, 'ntfs')
        self.cpu = GetSettings()._processor()
        self.partition_list = GetSettings()._partition()
        self.gpu_list = GetSettings()._vga_controller()

    def run(self):
        """Start the application."""

        # Ask questions to the user
        user = inquirer.prompt(question_manager(self),
                               theme=load_theme_from_dict(self.theme))

        # __TESTING__
        from pprint import pprint
        pprint(user)


if __name__ == '__main__':
    PyArchboot().run()


# PyArchboot - Python Arch Linux Installer by grm34 under Apache License 2.0
##############################################################################
