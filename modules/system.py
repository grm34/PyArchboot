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
import os
import re
from shlex import quote

from .unix_command import command_output, api_json_ouput


class get_settings:
    """Get required user settings."""

    def drive(self, trad):
        """Get available drives."""
        cmd = 'lsblk -I 8 -d -p -o NAME,SIZE,MODEL | grep -v NAME'
        output = command_output(cmd, exit_on_error=True)
        if output is not False:
            output = list(filter(None, output.split('\n')))
            output.insert(0, (trad('Use already formatted partitions'), None))

        return output

    def partition(self):
        """Get available partitions."""
        cmd = 'lsblk -p -l -o NAME,SIZE,FSTYPE,TYPE,MOUNTPOINT,MODEL'
        pipe = 'grep part | sed "s/part //g"'
        cmd = '{cmd} | {pipe}'.format(cmd=cmd, pipe=pipe)
        output = command_output(cmd)
        if output is not False:
            output = list(filter(None, output.split('\n')))

        return output

    def processor(self):
        """Get the processor."""
        cmd = 'cat /proc/cpuinfo | grep "model name" | uniq'
        output = command_output(cmd, exit_on_error=True)
        if output is not False:
            output = output.split('\n')[0].split(': ')[-1]
            output = re.sub(' +', ' ', output)

        return output

    def vga_controller(self):
        """Get available VGA controllers."""
        cmd = 'lspci | grep -e VGA -e 3D'
        pipe = 'sed "s/.*: //g" | sed "s/Graphics Controller //g"'
        cmd = '{cmd} | {pipe}'.format(cmd=cmd, pipe=pipe)
        output = command_output(cmd)
        if output is not False:
            output = list(filter(None, output.split('\n')))

        return output

    def filesystem(self, trad, arg):
        """Check for ntfs - lvm - luks."""
        msg_error = trad('No existing {arg} volume detected'.format(arg=arg))
        output = command_output('lsblk -f | grep {arg}'
                                .format(arg=arg, error=msg_error))
        if output is not False:
            output = True

        return output

    def firmware(self):
        """Get the system firmware."""
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

    def ipinfo(self):
        """Get user IP adress data."""
        output = api_json_ouput('https://ipinfo.io?token=26d03faada92e8',
                                exit_on_error=True,
                                error='no internet connection !', timeout=2)
        return output

    def mirrorlist(self, country):
        """Get user country mirrorlist."""
        url_base = 'https://www.archlinux.org/mirrorlist/'
        url_args = 'country={code}&use_mirror_status=on'.format(code=country)
        url = '{base}?{args}'.format(base=url_base, args=url_args)
        output = command_output('curl -s {url}'.format(url=quote(url)))
        if output is not False:
            output = output.replace('#Server =', 'Server =')

        return output


# PyArchboot - Python Arch Linux Installer by grm34 under Apache License 2.0
##############################################################################
