# -*- coding: utf-8 -*-

"""
Copyright 2020 Jeremy Pardo @grm34 https://github.com/grm34.

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
import sys
from shutil import copy2, copytree

import coloredlogs
import inquirer
from inquirer.themes import load_theme_from_dict
from termcolor import colored

from modules.app import app_banner, app_helper, app_reboot, app_translator
from modules.installer import (clean_pacman_cache,
                               configure_desktop_environment,
                               configure_display_manager, configure_grub,
                               configure_systemdboot, create_user,
                               generate_fstab, install_aur_helper,
                               install_base_system, install_grub_bootloader,
                               install_network, install_optional_packages,
                               set_hostname_file, set_locales, set_mirrorlist,
                               set_root_passwd, set_timezone,
                               set_user_privileges, set_virtual_console)
from modules.partitioner import (create_dos_partitions, create_lvm_partitions,
                                 delete_partitions, format_drive,
                                 format_partitions, mount_partitions,
                                 new_partition_table, set_partition_types,
                                 umount_partitions)
from modules.questioner.questions import question_manager
from modules.session import (clean_session, desktop_session, display_session,
                             drive_session, partition_session, system_session,
                             vga_session)
from modules.system_manager.settings import (get_drives, get_filesystem,
                                             get_firmware, get_ipinfo,
                                             get_mirrorlist, get_mountpoints,
                                             get_partition_id, get_partitions,
                                             get_partuuid, get_processor,
                                             get_swap, get_vga_controller,
                                             get_volumes)
from modules.system_manager.unix_command import dump_json_file, load_json_file

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
coloredlogs.install(level='INFO',
                    logger=console,
                    datefmt='%H:%M:%S',
                    fmt='[%(asctime)s] %(levelname)s > %(message)s',
                    level_styles={
                        'critical': {'bold': True, 'color': 'red'},
                        'debug': {'color': 'green'},
                        'error': {'color': 'red'},
                        'info': {'color': 'cyan'},
                        'warning': {'color': 'yellow', 'bold': True}},
                    field_styles={
                        'levelname': {'bold': True, 'color': 'green'},
                        'asctime': {'color': 'yellow'}})


class PyArchboot(object):
    """
    Application main object.

    Arch Linux is a light and fast distribution whose concept is to remain as
    simple as possible. In the same purpose and in order to give free choice
    to the users, this script performs a minimal arch installation, and only
    required packages will be installed. According to desired configuration
    and in order to get complete support additional packages may be required.

    Arguments
    ---------
        object: base class of the class hierarchy

    Parameters
    ----------
        self.app: "Application information" > dict()
        self.packages: "Arch Linux packages" > dict()
        self.theme: "Application theme" > dict()
        self.ipinfo: "User's IP address data" > dict()
        self.mirrorlist: "User's country mirrorlist" > str()
        self.trad: "Application language" > func()
        self.cpu: "User's processor" > str()
        self.efi: "User's firmware version" > str()
        self.firmware: "User's firmware type" > str()
        self.gpu: "Available VGA controllers" > array()
        self.drives: "Available drives" > array()
        self.partitions: "Available partitions" > array()
        self.mountpoints: "Mountpoints of mounted partitions" > array()
        self.volumes: "Existing LVM volumes" > array()
        self.lvm: "Support for LVM volumes" > bool()
        self.luks: "Support for encrypted drives" > bool()
        self.ntfs: "Support for NTFS partitions" > bool()
        self.user: "User's session parameters" > dict()

    Project structure
    -----------------
        " PyArchboot.py
        " |---` modules/
        " |     |---- questioner/
        " |     |     |---- __init__.py
        " |     |     |---- questions.py
        " |     |     |---- updater.py
        " |     |     |---- validator.py
        " |     |
        " |     |---- system_manager/
        " |     |     |---- __init__.py
        " |     |     |---- settings.py
        " |     |     |---- unix_command.py
        " |     |
        " |     |---- __init__.py
        " |     |---- app.py
        " |     |---- installer.py
        " |     |---- partitioner.py
        " |     |---- session.py
        "`
    """

    def __init__(self):
        """
        Set main class instance.

        Initialize
        ----------
            Accessible attributes of the class
        """
        # Application parameters
        self.app = load_json_file('app.json')
        app_banner(self)
        options = app_helper(self)
        self.packages = load_json_file('packages.json')
        themes = load_json_file('themes.json')

        # User parameters
        self.theme = themes['default']
        self.ipinfo = get_ipinfo(self)
        self.mirrorlist = get_mirrorlist(self)
        language = self.ipinfo['country'].lower()
        if options.lang:
            language = options.lang[0].strip()
        self.trad = app_translator(language)
        if options.theme:
            self.theme = themes[options.theme[0].strip()]

        # Session parameters
        self.cpu = get_processor(self)
        self.efi, self.firmware = get_firmware(self)
        self.controllers = get_vga_controller(self)
        self.drives = get_drives(self)
        self.partitions = get_partitions(self)
        self.mountpoints = get_mountpoints(self)
        self.volumes = get_volumes(self)
        self.lvm = get_filesystem(self, 'lvm')
        self.luks = get_filesystem(self, 'luks')
        self.ntfs = get_filesystem(self, 'ntfs')
        self.user = {}

    def run(self):
        """
        Start the application.

        Actions
        -------
            1) Ask questions to the user.
            2) Set parameters of the current session.
            3) Partition the disk (optional).
            4) Mount the partitions.
            5) Install Arch Linux.
        """
        # Ask questions to the user by running questioner module
        self.user = inquirer.prompt(question_manager(self),
                                    theme=load_theme_from_dict(self.theme))

        if self.user['confirm'] is False:
            del self
            os.execl(sys.executable, sys.executable, * sys.argv)

        # Set parameters of the current session
        session_manager = [drive_session(self),
                           partition_session(self),
                           vga_session(self),
                           desktop_session(self),
                           display_session(self),
                           system_session(self),
                           clean_session(self)]

        for session in session_manager:
            self.user = session

        # Umount user's partitions
        umount_partitions(self)

        # Partition the disk (optional)
        if self.user['drive']['name'] is not None:
            delete_partitions(self)
            format_drive(self)
            new_partition_table(self)
            create_dos_partitions(self)
            self.user['partitions']['drive_id'] = get_partition_id(self)
            self.user['partitions']['partuuid'] = get_partuuid(self)
            set_partition_types(self)
            if self.user['drive']['lvm'] is True:
                create_lvm_partitions(self)
                self.user['partitions']['drive_id'] = get_partition_id(self)
                self.user['partitions']['partuuid'] = get_partuuid(self)
            format_partitions(self)

        # Mount the partitions
        mount_partitions(self)

        # Install Arch Linux
        functions = [set_mirrorlist(self), install_base_system(self),
                     generate_fstab(self), set_timezone(self),
                     set_locales(self), set_virtual_console(self),
                     set_hostname_file(self), set_root_passwd(self),
                     create_user(self), install_network(self),
                     install_grub_bootloader(self),
                     install_optional_packages(self),
                     configure_systemdboot(self), configure_grub(self),
                     configure_desktop_environment(self),
                     configure_display_manager(self),
                     set_user_privileges(self), install_aur_helper(self),
                     clean_pacman_cache(self)]

        for function in functions:
            cmd = function

        # Copy logs to system
        logging.info(trad('installation successfull'))
        dump_json_file('{x}.log'.format(x=self.user['username']), self.user)
        copytree('{path}/logs'.format(path=os.getcwd()),
                 '/mnt/var/log/PyArchboot',
                 copy_function=copy2)

        # Reboot the system
        message = self.trad('Do you wish to reboot your computer now')
        question = [inquirer.Confirm('reboot', message=message, default=True)]
        confirm = inquirer.prompt(question,
                                  theme=load_theme_from_dict(self.theme))

        if confirm['reboot'] is True:
            app_reboot()
        else:
            sys.exit(0)


if __name__ == '__main__':
    if not os.geteuid() == 0:
        sys.exit(colored('ERROR: This script must be run as root !',
                         'red',
                         attrs=['bold']))
    PyArchboot().run()


# PyArchboot - Python Arch Linux Installer by grm34 under Apache License 2.0
##############################################################################
