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
from shlex import quote

from .unix_command import api_json_ouput, command_output


class GetSettings:
    """Class to get user's system settings."""

    def _drive(self, trad):
        """Get user's available drives.

        Arguments:
            trad -- Function to translate string

        Submodules:
            command_output -- Subprocess check_output with return codes

        Returns:
            output -- Array containing the available drives plus an option
                      to select already formatted partitions
        """
        cmd = 'lsblk -I 8 -d -p -o NAME,SIZE,MODEL | grep -v NAME'
        output = command_output(cmd, exit_on_error=True)
        if output is not False:
            output = list(filter(None, output.split('\n')))
            output.insert(0, (trad('Use already formatted partitions'), None))

        return output

    def _partition(self):
        """Get user's available partitions.

        Submodules:
            command_output -- Subprocess check_output with return codes

        Returns:
            output -- Array containing the available partitions
        """
        cmd = 'lsblk -p -l -o NAME,SIZE,FSTYPE,TYPE,MOUNTPOINT,MODEL'
        pipe = 'grep part | sed "s/part //g"'
        cmd = '{cmd} | {pipe}'.format(cmd=cmd, pipe=pipe)
        output = command_output(cmd)
        if output is not False:
            output = list(filter(None, output.split('\n')))

        return output

    def _processor(self):
        """Get user's processor.

        Modules:
            re -- Regular expression matching operations

        Submodules:
            command_output -- Subprocess check_output with return codes

        Returns:
            output -- String containing the processor model name
        """
        cmd = 'cat /proc/cpuinfo | grep "model name" | uniq'
        output = command_output(cmd, exit_on_error=True)
        if output is not False:
            output = output.split('\n')[0].split(': ')[-1]
            output = re.sub(' +', ' ', output)

        return output

    def _vga_controller(self):
        """Get user's available VGA controllers.

        Submodules:
            command_output -- Subprocess check_output with return codes

        Returns:
            output -- Array containing the available VGA controllers
        """
        cmd = 'lspci | grep -e VGA -e 3D'
        pipe = 'sed "s/.*: //g" | sed "s/Graphics Controller //g"'
        cmd = '{cmd} | {pipe}'.format(cmd=cmd, pipe=pipe)
        output = command_output(cmd)
        if output is not False:
            output = list(filter(None, output.split('\n')))

        return output

    def _filesystem(self, trad, arg):
        """Check if a filesystem is used by a volume or a partition.

        Used to check if user as ntfs, lvm or encrypted volumes to get thoses
        volumes supported by the system (by installing the required packages)

        Arguments:
            trad -- Function to translate string;
            arg -- String containing the filesystem to check

        Submodules:
            command_output -- Subprocess check_output with return codes

        Returns:
            output -- Boolean (True or False)
        """
        msg_error = trad('No existing {arg} volume detected'.format(arg=arg))
        output = command_output('lsblk -f | grep {arg}'
                                .format(arg=arg, error=msg_error))
        if output is not False:
            output = True

        return output

    def _firmware(self):
        """Get user's system firmware.

        Modules:
            os -- Export all functions from posix

        Returns:
            efi, firmware -- Strings containing system firmware type
        """
        if os.path.isdir('/sys/firmware/efi/efivars'):
            firmware = 'uefi'
            if '64' in open('/sys/firmware/efi/fw_platform_size').read():
                efi = 'x64'
            else:
                efi = 'x86'
        else:
            efi = None
            firmware = 'bios'

        return efi, firmware

    def _ipinfo(self):
        """Get user's IP address data.

        Submodules:
            api_json_output -- JSON API url parser

        Returns:
            output -- Dictionary containing IP address data
        """
        output = api_json_ouput('https://ipinfo.io?token=26d03faada92e8',
                                exit_on_error=True,
                                error='no internet connection !', timeout=2)
        return output

    def _mirrorlist(self, country):
        """Get user's fastest mirrors (corresponding to country).

        Arguments:
            country -- String containing user's country

        Modules:
            shlex.quote -- Return a shell-escaped version of the string

        Submodules:
            command_output -- Subprocess check_output with return codes

        Returns:
            output -- String containing the list of the mirrors
        """
        url_base = 'https://www.archlinux.org/mirrorlist/'
        url_args = 'country={code}&use_mirror_status=on'.format(code=country)
        url = '{base}?{args}'.format(base=url_base, args=url_args)
        output = command_output('curl -s {url}'.format(url=quote(url)))
        if output is not False:
            output = output.replace('#Server =', 'Server =')

        return output


# PyArchboot - Python Arch Linux Installer by grm34 under Apache License 2.0
##############################################################################
