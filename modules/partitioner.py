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
import time
from shlex import quote

from humanfriendly import parse_size, round_number

from .system_manager.settings import GetSettings
from .system_manager.unix_command import command_output, run_command


def umount_partitions(self):
    """
    Umount user's existing partitions.

    Modules
    -------
        logging: "Event logging system for applications and libraries"
        time: "Various functions to manipulate time values"

    Submodules
    ----------
        `GetSettings`: "Class to get user's system settings"
        `run_command`: "Subprocess Popen with console output"
    """
    for partition in self.mountpoints:

        # Deactivate swap
        if 'swap' in partition.lower():
            mountpoint = GetSettings()._swap()
            if mountpoint is not False:
                logging.info(self.trad('deactivate swap partition [{id}]')
                             .format(id=mountpoint[0].split()[0]))

                cmd = run_command('swapoff -a {swap}'
                                  .format(swap=mountpoint[0].split()[0]))

        # Umount the partitions
        if ('archiso' not in partition.lower()) and \
                ('swap' not in partition.lower()):

            logging.info(self.trad('umount {id}').format(id=partition))
            cmd = run_command('umount -f -R -q {id}'.format(id=partition))
            time.sleep(1)


def delete_partitions(self):
    """
    Delete existing partitions of the user's selected drive.

    Modules
    -------
        logging: "Event logging system for applications and libraries"
        time: "Various functions to manipulate time values"

    Submodules
    ----------
        `GetSettings`: "Class to get user's system settings"
        `run_command`: "Subprocess Popen with console output"
    """
    # Delete lvm partitions
    for partition in list(set(self.volumes[0])):
        if self.user['drive']['name'] in partition:
            partition = partition.split('//')[0].strip()
            logging.info(self.trad('delete {lv}').format(lv=partition))
            cmd = run_command('lvremove -q -f -y {lv}'.format(lv=partition))
            time.sleep(1)

    # Delete volume groups
    for volume in list(set(self.volumes[1])):
        if self.user['drive']['name'] in volume:
            volume = volume.split('/')[0].strip()
            logging.info(self.trad('delete {vg}').format(vg=volume))
            cmd = run_command('vgremove -q -f -y {vg}'.format(vg=volume))
            time.sleep(1)

    # Delete physical volumes
    for volume in list(set(self.volumes[0])):
        if self.user['drive']['name'] in volume:
            volume = volume.strip()
            logging.info(self.trad('delete {pv}').format(pv=volume))
            cmd = run_command('pvremove -q -f -y {pv}'.format(pv=volume))
            time.sleep(1)

    # Delete DOS partitions
    dos_partitions = GetSettings()._partition_ids(self.user['drive']['name'])
    for partition in dos_partitions:
        logging.info(self.trad('delete {dos}').format(dos=partition))
        pipe = ['/usr/bin/printf', 'd\n\nw']
        cmd = 'fdisk --wipe=always {drive}'.format(
            drive=self.user['drive']['name'])
        cmd = run_command(cmd, args=pipe)
        time.sleep(1)


def format_drive(self):
    """
    Wipe and format drive.

    Modules
    -------
        shlex.quote: "Return a shell-escaped version of the string"
        logging: "Event logging system for applications and libraries"
        time: "Various functions to manipulate time values"

    Submodules
    ----------
        `run_command`: "Subprocess Popen with console output"
        `command_output`: "Subprocess `check_output` with return codes"
    """
    logging.info(self.trad('format {drive} [{size}]')
                 .format(drive=self.user['drive']['name'],
                         size=self.user['drive']['size']))

    cmd = run_command('wipefs -f -a {drive}'
                      .format(drive=self.user['drive']['name']))

    cmd = 'dd if=/dev/zero of={drive} bs=512 count=1 conv=notrunc'.format(
        drive=quote(self.user['drive']['name']))

    cmd = command_output(cmd, exit_on_error=True)
    time.sleep(1)


def new_partition_table(self):
    """
    Create new partition table on user's selected drive.

    Modules
    -------
        logging: "Event logging system for applications and libraries"
        time: "Various functions to manipulate time values"

    Submodules
    ----------
        `run_command`: "Subprocess Popen with console output"
    """
    logging.info(self.trad('create new {table} partition table on {drive}')
                 .format(table=self.user['drive']['table'].upper(),
                         drive=self.user['drive']['name']))

    pipe = ['/usr/bin/printf', 'label: {table}'.format(
        table=self.user['drive']['table'])]

    cmd = 'sfdisk -f -q --wipe=always {drive}'.format(
        drive=self.user['drive']['name'])

    cmd = run_command(cmd, args=pipe, exit_on_error=True)
    time.sleep(1)


def create_dos_partitions(self):
    """
    Create dos partition on user's selected drive.

    Modules
    -------
        humanfriendly: "Human readable data libraries"
        logging: "Event logging system for applications and libraries"
        time: "Various functions to manipulate time values"

    Submodules
    ----------
        `run_command`: "Subprocess Popen with console output"
    """
    for partition, size in zip(self.user['partitions']['name'],
                               self.user['partitions']['size']):

        logging.info(self.trad(
            'create {partition} partition [{size}] on {drive}').format(
                partition=partition,
                size=size,
                drive=self.user['drive']['name']))

        if size == 'freespace' or \
                ((self.user['drive']['lvm'] is True) and
                 (partition == 'root')):
            size = '16T'

        size = parse_size(size.replace(',', '.'))
        size = round_number(size / 1000)

        pipe = ['/usr/bin/printf', 'size={size}K'.format(size=size)]
        cmd = 'sfdisk -f -q --no-reread -W always --append {drive}'.format(
            drive=self.user['drive']['name'])

        cmd = run_command(cmd, args=pipe, exit_on_error=True)
        time.sleep(1)


def set_partition_types(self):
    """
    Set type of user's dos partitions.

    Modules
    -------
        logging: "Event logging system for applications and libraries"
        time: "Various functions to manipulate time values"

    Submodules
    ----------
        `run_command`: "Subprocess Popen with console output"
    """
    for partition, drive_id in zip(self.user['partitions']['name'],
                                   self.user['partitions']['drive_id']):

        if (self.firmware == 'uefi') and (partition == 'boot'):
            gdisk_pipe = 't\nef00\nw'

        elif (self.user['drive']['lvm'] is True) and (partition == 'root'):
            gdisk_pipe = 't\n1\n8e00\nw'

        if 'gdisk_pipe' in locals():
            logging.info(self.trad(
                'set LVM partition type for {name} partition [{id}]').format(
                    name=partition, id=drive_id))

            pipe = ['/usr/bin/printf', gdisk_pipe]
            cmd = 'gdisk {drive}'.format(drive=self.user['drive']['name'])
            cmd = run_command(cmd, args=pipe, exit_on_error=True)

            del gdisk_pipe
            time.sleep(1)


def create_lvm_partitions(self):
    """
    Create LVM partitions on user's selected drive.

    Modules
    -------
        logging: "Event logging system for applications and libraries"
        time: "Various functions to manipulate time values"

    Submodules
    ----------
        `run_command`: "Subprocess Popen with console output"
    """
    for partition, drive_id, size in zip(self.user['partitions']['name'],
                                         self.user['partitions']['drive_id'],
                                         self.user['partitions']['size']):

        # Create LVM Volumes on root partition (dos)
        if partition == 'root':

            # LVM on LUKS
            if self.user['drive']['luks'] is True:

                logging.info(self.trad('create LVM on LUKS [{id}]')
                             .format(id=drive_id))

                cmd_list = [
                    'cryptsetup luksFormat {id}'.format(id=drive_id),
                    'cryptsetup open {id} cryptlvm'.format(id=drive_id),
                    'pvcreate -y /dev/mapper/cryptlvm',
                    'vgcreate -y lvm /dev/mapper/cryptlvm']

            # LVM without LUKS
            else:
                logging.info(self.trad('create LVM Volume [{id}]')
                             .format(id=drive_id))

                cmd_list = ['pvcreate -y {id}'.format(id=drive_id),
                            'vgcreate -y lvm {id}'.format(id=drive_id)]

            # Create Volumes
            for cmd in cmd_list:
                cmd = run_command(cmd, exit_on_error=True)

        # Create LVM partitions
        elif partition != 'boot':

            logging.info(self.trad(
                'create {partition} LVM partition [{size}]').format(
                    partition=partition, size=size))

            if size == 'freespace':
                size = '-l 100%FREE'
            else:
                size = '-L {size}'.format(size=size)

            cmd = run_command('lvcreate -y {size} -n {name} lvm'
                              .format(size=size, name=partition),
                              exit_on_error=True)
        time.sleep(1)


def format_partitions(self):
    """
    Format created partitions of user's selected drive.

    Modules
    -------
        logging: "Event logging system for applications and libraries"

    Submodules
    ----------
        `command_output`: "Subprocess `check_output` with return codes"
    """
    for partition, drive_id, size, filesystem in zip(
            self.user['partitions']['name'],
            self.user['partitions']['drive_id'],
            self.user['partitions']['size'],
            self.user['partitions']['filesystem']):

        logging.info(self.trad(
            'format {partition} partition [{filesystem} - {size}]').format(
                partition=partition, filesystem=filesystem, size=size))

        if filesystem == 'fat32':
            filesystem = 'fat -F32'

        if partition == 'swap':
            cmd = 'yes | mkswap {id}'.format(id=drive_id)
        else:
            cmd = 'yes | mkfs.{filesystem} {id}'.format(filesystem=filesystem,
                                                        id=drive_id)
        cmd = command_output(cmd, exit_on_error=True)


def mount_partitions(self):
    """
    Mount the partitions and activate SWAP.

    Modules
    -------
        os: "Export all functions from posix"
        logging: "Event logging system for applications and libraries"
        time: "Various functions to manipulate time values"

    Submodules
    ----------
        `run_command`: "Subprocess Popen with console output"
    """
    for mountorder, partition, drive_id, mountpoint in sorted(
            zip(self.user['partitions']['mountorder'],
                self.user['partitions']['name'],
                self.user['partitions']['drive_id'],
                self.user['partitions']['mountpoint'])):

        logging.info(self.trad(
            'mount {partition} partition [{id}] on {mountpoint}').format(
                partition=partition, mountpoint=mountpoint, id=drive_id))

        if partition == 'swap':
            cmd = run_command('swapon {id}'.format(id=drive_id),
                              exit_on_error=True)
        else:
            if not os.path.exists(mountpoint):
                os.makedirs(mountpoint)

            cmd = run_command('mount {id} {mountpoint}'
                              .format(id=drive_id, mountpoint=mountpoint),
                              exit_on_error=True)
        time.sleep(1)


# PyArchboot - Python Arch Linux Installer by grm34 under Apache License 2.0
##############################################################################
