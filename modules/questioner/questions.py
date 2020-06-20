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
import re

import inquirer
from humanfriendly import format_size, parse_size
from inquirer.errors import ValidationError

from .updater import desktop_extra_assigner, partition_list_updater
from .validator import (hostname_validator, language_validator,
                        passwd_validator, size_validator, timezone_validator,
                        username_validator)


def question_manager(self):
    """[summary]
    """
    questions = [
        inquirer.List(
            'drive',
            message=self.trad('Select the drive to use'),
            choices=self.drive_list,
            carousel=True),
        inquirer.Confirm(
            'lvm',
            message=self.trad(
                'Do you wish to use Logical Volume Manager (LVM)'),
            ignore=lambda user:
                user['drive'] is None or self.firmware == 'bios'),
        inquirer.Confirm(
            'luks',
            message=self.trad(
                'Do you wish to encrypt the drive (LVM on LUKS)'),
            ignore=lambda user: user['lvm'] is False),
        inquirer.Checkbox(
            'optional_partitions',
            message=self.trad('Select optional partitions'),
            choices=['Swap', 'Home'],
            default=None),
        inquirer.Text(
            'boot_size',
            message=self.trad('Enter desired size for boot partition'),
            validate=lambda user,response:
                size_validator(self, user, response),
            ignore=lambda user: user['drive'] is None),
        inquirer.Confirm(
            'root_freespace',
            message=self.trad(
                'Do you wish use free space for root partition'),
            ignore=lambda user:
                user['drive'] is None
                or 'Home' in user['optional_partitions']),
        inquirer.Text(
            'root_size',
            message=self.trad('Enter desired size for root partition'),
            default=None,
            validate=size_validator,
            ignore=lambda user:
                user['drive'] is None or user['root_freespace'] is True),
        inquirer.Text(
            'swap_size',
            message=self.trad('Enter desired size for swap partition'),
            default=None,
            validate=size_validator,
            ignore=lambda user:
                user['drive'] is None
                or 'Swap' not in user['optional_partitions']),
        inquirer.Confirm(
            'home_freespace',
            message=self.trad(
                'Do you wish use free space for home partition'),
            ignore=lambda user:
                user['drive'] is None
                or 'Home' not in user['optional_partitions']),
        inquirer.Text(
            'home_size',
            message=self.trad('Enter desired size for home partition'),
            validate=size_validator,
            ignore=lambda user:
                user['drive'] is None
                or 'Home' not in user['optional_partitions']
                or user['home_freespace'] is True),
        inquirer.List(
            'boot_id',
            message=self.trad('Select boot partition'),
            choices=self.partition_list,
            carousel=True,
            ignore=lambda user:
                user['drive'] is not None or self.partition_list is None),
        inquirer.List(
            'root_id',
            message=self.trad('Select root partition'),
            choices=partition_list_updater,
            carousel=True,
            ignore=lambda user:
                user['drive'] is not None or self.partition_list is None),
        inquirer.List(
            'swap_id',
            message=self.trad('Select swap partition'),
            choices=partition_list_updater,
            carousel=True,
            ignore=lambda user:
                user['drive'] is not None
                or 'Swap' not in user['optional_partitions']),
        inquirer.List(
            'home_id',
            message=self.trad('Select home partition'),
            choices=partition_list_updater,
            carousel=True,
            ignore=lambda user:
                user['drive'] is not None
                or 'Home' not in user['optional_partitions']),
        inquirer.List(
            'timezone',
            message=self.trad('Select timezone'),
            choices=[self.ipinfo['timezone'],
                     (self.trad('Custom timezone'), None)],
            default=self.ipinfo['timezone'],
            carousel=True),
        inquirer.Text(
            'timezone',
            message=self.trad('Enter desired timezone'),
            validate=timezone_validator,
            ignore=lambda user: user['timezone'] is not None),
        inquirer.Text(
            'language',
            message=self.trad('Enter language code'),
            validate=language_validator),
        inquirer.Text(
            'hostname',
            message=self.trad('Enter hostname'),
            validate=hostname_validator),
        inquirer.Password(
            'root_passwd',
            message=self.trad('Enter password for root'),
            validate=passwd_validator),
        inquirer.Text(
            'username',
            message=self.trad('Enter username'),
            validate=username_validator),
        inquirer.Password(
            'user_passwd',
            message=self.trad('Enter password for user {username}'),
            validate=passwd_validator),
        inquirer.List(
            'kernel',
            message=self.trad('Select Linux Kernel'),
            choices=[('Linux Stable', 0), ('Linux Hardened', 1),
                     ('Linux LTS', 2), ('Linux ZEN', 3)],
            carousel=True),
        inquirer.Confirm(
            'firmware',
            message=self.trad('Do you wish to install Linux Firmware'),
            default=True),
        inquirer.List(
            'desktop',
            message=self.trad('Select Desktop Environment'),
            choices=[None, ('Gnome', 0), ('KDE', 1), ('Deepin', 2), ('Mate', 3),
                     ('XFCE', 4), ('LXQT', 5), ('LXDE', 6), ('Cinnamon', 7),
                     ('Budgie', 8), ('Enlightenment', 9), ('Awesome', 10),
                     ('Xmonad', 11), ('i3', 12)],
            carousel=True),
        inquirer.Confirm(
            'desktop_extra',
            message=desktop_extra_assigner,
            ignore=lambda user:
                user['desktop'] is None
                or user['desktop'] not in [0, 1, 2, 3, 4]),
        inquirer.List(
            'display',
            message=self.trad('Select Display Manager'),
            choices=[('Gdm', 0), ('LightDM', 1), ('Sddm', 2),
                     ('Lxdm', 3), ('Xdm', 4)],
            carousel=True,
            ignore=lambda user: user['desktop'] is None),
        inquirer.List(
            'greeter',
            message=self.trad('Select LightDM Greeter'),
            choices=[('Gtk', 0), ('Pantheon', 1), ('Deepin', 2),
                     ('Webkit', 3), ('Litarvan', 4)],
            carousel=True,
            ignore=lambda user:
                user['desktop'] is None or user['display'] != 1),
        inquirer.Confirm(
            'gpu_driver',
            message=self.trad('Do you wish to install GPU driver'),
            ignore=lambda user:
                user['desktop'] is None or self.gpu_list == ['']
                or self.gpu_list is False),
        inquirer.List(
            'vga_controller',
            message=self.trad('Select GPU Controller'),
            choices=self.gpu_list,
            carousel=True,
            ignore=lambda user: user['gpu_driver'] is False),
        inquirer.Confirm(
            'hardvideo',
            message=self.trad(
                'Do you wish to install Hardware video acceleration'),
            ignore=lambda user: user['gpu_driver'] is False),
        inquirer.Confirm(
            'gpu_proprietary',
            message=self.trad('Do you wish to install proprietary drivers'),
            ignore=lambda user:
                user['gpu_driver'] is False
                or 'nvidia' not in user['vga_controller'].lower()),
        inquirer.List(
            'aur_helper',
            message=self.trad('Select AUR Helper'),
            choices=[None, 'Yay', 'Pamac-aur', 'Trizen',
                     'Pacaur', 'Pakku', 'Pikaur'],
            carousel=True),
        inquirer.Confirm(
            'power',
            message=self.trad(
                'Do you wish add to all groups user {username}'),
            default=True)
    ]

    return questions


# PyArchboot - Python Arch Linux Installer by grm34 under Apache License 2.0
##############################################################################
