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

import inquirer

from .updater import desktop_extra_assigner, partition_list_updater
from .validator import (hostname_validator, language_validator,
                        passwd_validator, size_validator, timezone_validator,
                        username_validator)


def question_manager(self):
    """Ask questions to the user and store the answers.

    Modules:
        inquirer -- Common interactive command line user interfaces

    Submodules:
        desktop_extra_assigner -- Assign the extra packages name of the
                                  selected desktop;
        partition_list_updater -- Delete previous partition to display an
                                  updated array after selection;
        hostname_validator -- Match UNIX hostname regex;
        language_validator -- Match language code in libraries/locale;
        passwd_validator -- Match UNIX password regex;
        size_validator -- Match regex, current partition min/max size and
                          remaining disk space;
        timezone_validator -- Match timezone code in libraries/timezone;
        username_validator -- Match UNIX username regex

    Returns:
        questions -- Dictionary containing user's answers
    """
    logging.info(self.trad('use arrow keys to select an option'))
    logging.warning(self.trad('all data will be lost !'))

    questions = [

        # Drive
        inquirer.List(
            'drive',
            message=self.trad('Select the drive to use'),
            choices=self.drive_list,
            carousel=True),

        # Lvm
        inquirer.Confirm(
            'lvm',
            message=self.trad(
                'Do you wish to use Logical Volume Manager (LVM)'),
            ignore=lambda user:
                user['drive'] is None or self.firmware == 'bios'),

        # Luks
        inquirer.Confirm(
            'luks',
            message=self.trad(
                'Do you wish to encrypt the drive (LVM on LUKS)'),
            ignore=lambda user: user['lvm'] is False),

        # Optional partitions
        inquirer.Checkbox(
            'optional_partitions',
            message=self.trad('Select optional partitions'),
            choices=['Swap', 'Home'],
            default=None),

        # Boot size
        inquirer.Text(
            'boot_size',
            message=self.trad('Enter desired size for boot partition'),
            validate=lambda user, response:
                size_validator(self, user, response),
            ignore=lambda user: user['drive'] is None),

        # Root freespace
        inquirer.Confirm(
            'root_freespace',
            message=self.trad(
                'Do you wish use free space for root partition'),
            ignore=lambda user:
                user['drive'] is None or
                'Home' in user['optional_partitions']),

        # Root size
        inquirer.Text(
            'root_size',
            message=self.trad('Enter desired size for root partition'),
            default=None,
            validate=lambda user, response:
                size_validator(self, user, response),
            ignore=lambda user:
                user['drive'] is None or user['root_freespace'] is True),

        # Swap size
        inquirer.Text(
            'swap_size',
            message=self.trad('Enter desired size for swap partition'),
            default=None,
            validate=lambda user, response:
                size_validator(self, user, response),
            ignore=lambda user:
                user['drive'] is None or
                'Swap' not in user['optional_partitions']),

        # Home freespace
        inquirer.Confirm(
            'home_freespace',
            message=self.trad(
                'Do you wish use free space for home partition'),
            ignore=lambda user:
                user['drive'] is None or
                'Home' not in user['optional_partitions']),

        # Home size
        inquirer.Text(
            'home_size',
            message=self.trad('Enter desired size for home partition'),
            validate=lambda user, response:
                size_validator(self, user, response),
            ignore=lambda user:
                user['drive'] is None or
                'Home' not in user['optional_partitions'] or
                user['home_freespace'] is True),

        # Boot drive ID
        inquirer.List(
            'boot_id',
            message=self.trad('Select boot partition'),
            choices=self.partition_list,
            carousel=True,
            ignore=lambda user:
                user['drive'] is not None or self.partition_list is None),

        # Root drive ID
        inquirer.List(
            'root_id',
            message=self.trad('Select root partition'),
            choices=lambda user: partition_list_updater(self, user),
            carousel=True,
            ignore=lambda user:
                user['drive'] is not None or self.partition_list is None),

        # Swap drive ID
        inquirer.List(
            'swap_id',
            message=self.trad('Select swap partition'),
            choices=lambda user: partition_list_updater(self, user),
            carousel=True,
            ignore=lambda user:
                user['drive'] is not None or
                'Swap' not in user['optional_partitions']),

        # Home drive ID
        inquirer.List(
            'home_id',
            message=self.trad('Select home partition'),
            choices=lambda user: partition_list_updater(self, user),
            carousel=True,
            ignore=lambda user:
                user['drive'] is not None or
                'Home' not in user['optional_partitions']),

        # Timezone selection
        inquirer.List(
            'timezone',
            message=self.trad('Select timezone'),
            choices=[self.ipinfo['timezone'],
                     (self.trad('Custom timezone'),
                      None)],
            default=self.ipinfo['timezone'],
            carousel=True),

        # Custom timezone
        inquirer.Text(
            'timezone',
            message=self.trad('Enter desired timezone'),
            validate=lambda user,response:
                timezone_validator(self, user, response),
            ignore=lambda user: user['timezone'] is not None),

        # Language code
        inquirer.Text(
            'language',
            message=self.trad('Enter language code'),
            validate=lambda user,response:
                language_validator(self, user, response)),

        # Hostname
        inquirer.Text(
            'hostname',
            message=self.trad('Enter hostname'),
            validate=lambda user,response:
                hostname_validator(self, user, response)),

        # Root passwd
        inquirer.Password(
            'root_passwd',
            message=self.trad('Enter password for root'),
            validate=lambda user,response:
                passwd_validator(self, user, response)),

        # Username
        inquirer.Text(
            'username',
            message=self.trad('Enter username'),
            validate=lambda user,response:
                username_validator(self, user, response)),

        # User passwd
        inquirer.Password(
            'user_passwd',
            message=self.trad('Enter password for user {username}'),
            validate=lambda user,response:
                passwd_validator(self, user, response)),

        # Kernel
        inquirer.List(
            'kernel',
            message=self.trad('Select Linux Kernel'),
            choices=[('Linux Stable', 0),
                     ('Linux Hardened', 1),
                     ('Linux LTS', 2),
                     ('Linux ZEN', 3)],
            carousel=True),

        # Firmware drivers
        inquirer.Confirm(
            'firmware',
            message=self.trad('Do you wish to install Linux Firmware'),
            default=True),

        # Desktop environment
        inquirer.List(
            'desktop',
            message=self.trad('Select Desktop Environment'),
            choices=[None,
                     ('Gnome', 0),
                     ('KDE', 1),
                     ('Deepin', 2),
                     ('Mate', 3),
                     ('XFCE', 4),
                     ('LXQT', 5),
                     ('LXDE', 6),
                     ('Cinnamon', 7),
                     ('Budgie', 8),
                     ('Enlightenment', 9),
                     ('Awesome', 10),
                     ('Xmonad', 11),
                     ('i3', 12)],
            carousel=True),

        # Desktop extras
        inquirer.Confirm(
            'desktop_extra',
            message=lambda user: desktop_extra_assigner(self, user),
            ignore=lambda user:
                user['desktop'] is None or
                user['desktop'] not in [0, 1, 2, 3, 4]),

        # Display manager
        inquirer.List(
            'display',
            message=self.trad('Select Display Manager'),
            choices=[('Gdm', 0),
                     ('LightDM', 1),
                     ('Sddm', 2),
                     ('Lxdm', 3),
                     ('Xdm', 4)],
            carousel=True,
            ignore=lambda user: user['desktop'] is None),

        # LightDM greeter
        inquirer.List(
            'greeter',
            message=self.trad('Select LightDM Greeter'),
            choices=[('Gtk', 0),
                     ('Pantheon', 1),
                     ('Deepin', 2),
                     ('Webkit', 3),
                     ('Litarvan', 4)],
            carousel=True,
            ignore=lambda user:
                user['desktop'] is None or user['display'] != 1),

        # GPU Driver
        inquirer.Confirm(
            'gpu_driver',
            message=self.trad('Do you wish to install GPU driver'),
            ignore=lambda user:
                user['desktop'] is None or
                self.gpu_list == [''] or
                self.gpu_list is False),

        # VGA Controller selection
        inquirer.List(
            'vga_controller',
            message=self.trad('Select GPU Controller'),
            choices=self.gpu_list,
            carousel=True,
            ignore=lambda user: user['gpu_driver'] is False),

        # Hardware video acceleration
        inquirer.Confirm(
            'hardvideo',
            message=self.trad(
                'Do you wish to install Hardware video acceleration'),
            ignore=lambda user: user['gpu_driver'] is False),

        # Proprietary drivers
        inquirer.Confirm(
            'gpu_proprietary',
            message=self.trad('Do you wish to install proprietary drivers'),
            ignore=lambda user:
                user['gpu_driver'] is False or
                'nvidia' not in user['vga_controller'].lower()),

        # AUR Helper
        inquirer.List(
            'aur_helper',
            message=self.trad('Select AUR Helper'),
            choices=[None,
                     'Yay',
                     'Pamac-aur',
                     'Trizen',
                     'Pacaur',
                     'Pakku',
                     'Pikaur'],
            carousel=True),

        # User groups
        inquirer.Confirm(
            'power',
            message=self.trad(
                'Do you wish add to all groups user {username}'),
            default=True)
    ]

    return questions


# PyArchboot - Python Arch Linux Installer by grm34 under Apache License 2.0
##############################################################################
