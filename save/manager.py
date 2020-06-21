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

import json
import logging
import os
from crypt import METHOD_SHA512, crypt, mksalt

import inquirer
from inquirer.themes import load_theme_from_dict

from .app import packages, theme, trad
from .questions import questions

#user, firmware, drive_list, lvm, luks, ntfs, mirrorlist = ['' for x in range(6)]


def drive_manager(self):
    """Append the disk."""
    if self.self.user['drive'] is not None:

        # Append drive
        self.self.user['drive'] = {'name': self.user['drive'].split()[0],
                         'size': self.user['drive'].split()[1],
                         'model': self.user['drive'].split()[2],
                         'boot': self.user['drive'].split()[0],
                         'lvm': self.user['lvm'], 'luks': self.user['luks']}

        # Append LVM packages
        if self.user['lvm'] is True:
            self.user['drive']['lvm'] = packages['lvm']

        # Append partition table
        if self.firmware == 'uefi':
            self.user['drive']['table'] = 'gpt'

        else:
            self.user['drive']['table'] = 'mbr'

    # Custom mode
    else:

        # Get boot drive
        boot = str(self.drive_list[0]).split()[0]
        for drive in self.drive_list:
            if str(drive).split()[0] in self.user['boot_id'].split()[0]:
                boot = str(drive).split()[0]
                break

        # Append drive
        self.user['drive'] = {'name': None, 'boot': boot, 'lvm': self.lvm,
                              'luks': self.luks}

        # Append LVM packages
        if self.lvm is True:
            self.user['drive']['lvm'] = packages['lvm']

    return self.user


def partition_manager(self):
    """Append the partitions."""
    if self.user['drive']['name'] is not None:

        # Set root size
        if self.user['root_freespace'] is True:
            self.user['root_size'] = 'freespace'

        # Append partitions
        self.user['partitions'] = {'name': ['boot', 'root'],
                              'size': [self.user['boot_size'],
                                       self.user['root_size']],
                              'filesystem': ['fat32', 'ext4'],
                              'mountpoint': ['/mnt/boot', '/mnt'],
                              'mountorder': [1, 0]}

        # Append swap
        if 'Swap' in self.user['optional_partitions']:
            self.user['partitions']['name'].insert(1, 'swap')
            self.user['partitions']['size'].insert(1, self.user['swap_size'])
            self.user['partitions']['filesystem'].insert(1, 'swap')
            self.user['partitions']['mountpoint'].insert(1, 'swap')
            self.user['partitions']['mountorder'].insert(1, 2)

        # Append home
        if 'Home' in self.user['optional_partitions']:
            self.user['partitions']['name'].append('home')
            if self.user['home_freespace'] is True:
                self.user['home_size'] = 'freespace'
            self.user['partitions']['size'].append(self.user['home_size'])
            self.user['partitions']['filesystem'].append('ext4')
            self.user['partitions']['mountpoint'].append('/mnt/home')
            self.user['partitions']['mountorder'].append(3)

    # Custom mode
    else:

        # Append partitions
        self.user['partitions'] = {'name': ['boot', 'root'],
                              'drive_id': [self.user['boot_id'].split()[0],
                                           self.user['root_id'].split()[0]],
                              'mountpoint': ['/mnt/boot', '/mnt'],
                              'mountorder': [1, 0]}

        # Append swap
        if self.user['swap_id'] is not None:
            self.user['partitions']['name'].insert(1, 'swap')
            self.user['partitions']['drive_id'].insert(1,
                                                  self.user['swap_id'].split()[0])
            self.user['partitions']['mountpoint'].insert(1, 'swap')
            self.user['partitions']['mountorder'].insert(1, 2)

        # Append home
        if self.user['home_id'] is not None:
            self.user['partitions']['name'].append('home')
            self.user['partitions']['drive_id'].append(
                self.user['home_id'].split()[0])
            self.user['partitions']['mountpoint'].append('/mnt/home')
            self.user['partitions']['mountorder'].append(3)

    return self.user


def vga_manager(self):
    """Append VGA controller."""
    gpu_driver = None
    if self.user['gpu_driver'] is True:

        # NVIDIA controller
        if 'nvidia' in self.user['vga_controller'].lower():

            if self.user['gpu_proprietary'] is True:
                hardvideo = packages['hardvideo'][3]

                if self.user['kernel'] == 'linux':
                    gpu_driver = packages['gpu_driver'][3]

                elif self.user['kernel'] == 'linux-lts':
                    gpu_driver = packages['gpu_driver'][4]

                else:
                    gpu_driver = packages['gpu_driver'][5]

            else:
                gpu_driver = packages['gpu_driver'][2]
                hardvideo = packages['hardvideo'][2]

        # AMD Controller
        elif ('ATI' in self.user['vga_controller']) or \
                ('AMD' in self.user['vga_controller']):

            gpu_driver = packages['gpu_driver'][1]
            hardvideo = packages['hardvideo'][1]

        # Intel controller
        elif 'intel' in self.user['vga_controller'].lower():
            gpu_driver = packages['gpu_driver'][0]
            hardvideo = packages['hardvideo'][0]

        # Unreconized controller
        else:
            gpu_driver = packages['gpu_driver'][6]
            hardvideo = packages['hardvideo'][4]

    # Append model with corresponding driver
    self.user['gpu'] = {'model': self.user['vga_controller'],
                   'driver': gpu_driver,
                   'hardvideo': self.user['hardvideo']}

    # Append hardware video acceleration
    if self.user['hardvideo'] is True:
        self.user['gpu']['hardvideo'] = hardvideo

    return self.user


def desktop_manager(self):
    """Append desktop environment."""
    self.user['desktop_environment'] = {'name': self.user['desktop']}
    if self.user['desktop'] is not None:

        if self.user['desktop'] in [10, 11, 12]:
            self.user['desktop_environment']['requirements'] = \
                '{xorg} {xinit} {numlock}'.format(xorg=packages['xorg'],
                                                  xinit=packages['xinit'],
                                                  numlock=packages['numlock'])
        else:
            self.user['desktop_environment']['requirements'] = \
                '{xinit} {numlock}'.format(xinit=packages['xorg'],
                                           numlock=packages['numlock'])

        self.user['desktop_environment']['name'] = \
            packages['desktop']['name'][self.user['desktop']]

        self.user['desktop_environment']['packages'] = \
            packages['desktop']['packages'][self.user['desktop']]

        if self.user['desktop_extra'] is True:
            self.user['desktop_environment']['packages'] += ' {extras}'.format(
                extras=packages['desktop']['extras'][self.user['desktop']])

        self.user['desktop_environment']['startcmd'] = \
            packages['desktop']['startcmd'][self.user['desktop']]

    return self.user


def display_manager(self):
    """Append the display manager."""
    self.user['display_manager'] = {'name': self.user['display']}

    if self.user['display'] is not None:
        self.user['display_manager']['name'] = \
            packages['display_manager']['name'][self.user['display']]

        self.user['display_manager']['packages'] = \
            packages['display_manager']['packages'][self.user['display']]

        if self.user['greeter'] is not None:
            self.user['display_manager']['packages'] += ' {greeter}'.format(
                greeter=packages['greeter']['packages'][self.user['greeter']])

            self.user['display_manager']['session'] = \
                packages['greeter']['session'][self.user['greeter']]

    return self.user


def system_manager(self):
    """Append kernel, cpu, passwords, keymap, ntfs, firmware and mirrors."""
    self.user['kernel'] = packages['kernel'][self.user['kernel']]

    # Processor
    if 'intel' in self.cpu.lower():
        self.user['cpu'] = {'name': self.cpu,
                            'microcode': packages['microcode'][0]}
    elif 'AMD' in self.cpu:
        self.user['cpu'] = {'name': self.cpu,
                            'microcode': packages['microcode'][1]}
    else:
        self.user['cpu'] = {'name': self.cpu, 'microcode': None}

    # Passwords
    rootpasswd = crypt(self.user['root_passwd'], mksalt(METHOD_SHA512))
    userpasswd = crypt(self.user['user_passwd'], mksalt(METHOD_SHA512))
    self.user['passwords'] = {'root': rootpasswd, 'user': userpasswd}

    # Keymap
    if 'keymap' not in locals():
        self.user['keymap'] = self.user['language'].split('_')[0]

    # Ntfs support
    self.user['ntfs'] = self.ntfs
    if self.ntfs is True:
        self.user['ntfs'] = packages['ntfs']

    # System firmware
    self.user['firmware'] = {'type': self.firmware, 'version': self.efi,
                        'driver': self.user['firmware']}

    if self.user['firmware']['driver'] is True:
        self.user['firmware']['driver'] = packages['firmware']

    # Mirrorlist
    self.user['mirrorlist'] = self.mirrorlist

    return self.user


def clean_dictionary(self):
    """Delete unused entries."""
    unused_entries = ['root_freespace', 'home_freespace', 'hardvideo',
                      'optional_partitions', 'boot_id', 'greeter', 'display',
                      'boot_size', 'root_size', 'swap_size', 'home_size',
                      'root_id', 'lvm', 'swap_id', 'home_id', 'luks',
                      'user_passwd', 'root_passwd', 'desktop', 'gpu_driver',
                      'vga_controller', 'gpu_proprietary', 'desktop_extra']

    for unused in unused_entries:
        del self.user[unused]

    return self.user


# PyArchboot - Python Arch Linux Installer by grm34 under Apache License 2.0
##############################################################################
