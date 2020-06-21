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

import gettext
import json
import logging
import os
import shlex
import sys
import time
from shlex import quote
from subprocess import PIPE, CalledProcessError, Popen, check_output

from humanfriendly import parse_size, round_number

# Load app settings
with open('{path}/json/app.json'.format(path=os.getcwd()), 'r',
          encoding='utf-8') as app_settings:
    app = json.load(app_settings)

# Load user settings
with open('{path}/json/settings.json'.format(path=os.getcwd()), 'r',
          encoding='utf-8') as settings:
    user = json.load(settings)

# Load app language
language = gettext.translation('PyArchboot', localedir='locales',
                               languages=['{lang}'.format(lang=app['lang'])])
trad = language.gettext


def command_output(cmd):
    """Get the output of an UNIX command.

    Arguments:
        cmd {string} -- quoted UNIX command
    """
    output = check_output(cmd, shell=False, encoding='utf-8')

    return output


# Get existings drives and partitions.
##############################################################################


def partition_drive_id():
    """Get partitions drive ID and returns to user dictionary."""
    x = 'lsblk -p -l -o NAME,TYPE {d} | grep part | sed "s/ part//g"'.format(
        d=quote(user['drive']['name']))

    drive_id_list = command_output(x).split('\n')
    user['partitions']['drive_id'] = list(filter(None, drive_id_list))
    return user


def partition_uuid():
    """Get partitions PARTUUID and returns to user dictionary."""
    partuuid_list = []
    for drive_id in user['partitions']['drive_id']:

        partuuid = command_output('blkid -o value -s PARTUUID {id}'
                                  .format(id=quote(drive_id))
                                  .replace('\n', ''))
        partuuid_list.append(partuuid)

    user['partitions']['partuuid'] = list(filter(None, partuuid_list))
    return user


# Get existing partitions of the selected drive
if user['drive']['name'] is not None:
    existing_partitions = partition_drive_id()

# Get mountpoints of existing partitions
cmd = 'lsblk -l -o MOUNTPOINT | grep -v MOUNTPOINT'
mounted_partitions = command_output(cmd).split('\n')
mounted_partitions = list(filter(None, mounted_partitions))

# Get existing LVM partitions
cmd = 'lvs --aligned --noheadings --separator / -o vg_name,lv_name'
lv_list = command_output(cmd).split('\n')
lv_list = list(filter(None, lv_list))

# Get existing volume groups
vg_list = command_output('vgs --noheadings -o vg_name').split('\n')
vg_list = list(filter(None, vg_list))

# Get existing physical groups
pv_list = command_output('pvs --noheadings -o pv_name').split('\n')
pv_list = list(filter(None, pv_list))


# Umount existing partitions.
##############################################################################
for partition in mounted_partitions:

    if 'swap' in partition.lower():
        cmd = 'lsblk -p -l -o NAME,MOUNTPOINT | grep SWAP'
        swapon = command_output(cmd).split('\n')
        swapon = list(filter(None, swapon))

        logging.info(trad('deactivate swap partition [{swap}]'
                          .format(swap=swapon[0].split()[0])))

        cmd = Popen(shlex.split('swapoff -a {swap}'
                                .format(swap=swapon[0].split()[0])),
                    stdin=PIPE, stdout=PIPE)

    if ('archiso' not in partition.lower()) and \
            ('swap' not in partition.lower()):

        logging.info(trad('umount {partition}').format(partition=partition))

        cmd_args = shlex.split('umount -f -A -R -q {partition}'.format(
            partition=partition))

        cmd = Popen(cmd_args, stdin=PIPE, stdout=PIPE)
        time.sleep(1)


# Prepare the drive (default mode: dedicated drive).
##############################################################################
if user['drive']['name'] is not None:

    # Delete existing partitions
    for lv in lv_list:
        logging.info(trad('delete {lv}').format(lv=lv))

        cmd_args = shlex.split('lvremove -q -f -y {lv}'.format(lv=lv))
        cmd = Popen(cmd_args, stdin=PIPE, stdout=PIPE)
        time.sleep(1)

    for vg in vg_list:
        logging.info(trad('delete {vg}').format(vg=vg))

        cmd_args = shlex.split('vgremove -q -f -y {vg}'.format(vg=vg))
        cmd = Popen(cmd_args, stdin=PIPE, stdout=PIPE)
        time.sleep(1)

    for pv in pv_list:
        logging.info(trad('delete {pv}').format(pv=pv))

        cmd_args = shlex.split('pvremove -q -f -y {pv}'.format(pv=pv))
        cmd = Popen(cmd_args, stdin=PIPE, stdout=PIPE)
        time.sleep(1)

    for partition in existing_partitions:
        logging.info(trad('delete {partition}').format(partition=partition))

        cmd_args1 = Popen(['/usr/bin/printf', 'd\n\nw'], stdout=PIPE)
        cmd_args2 = Popen(shlex.split('fdisk --wipe=always {drive}'
                                      .format(drive=user['drive']['name'])),
                          stdin=cmd_args1.stdout, stdout=PIPE)

        cmd = cmd_args2.communicate()[0]
        time.sleep(1)

    # Format the disk
    logging.info(
        trad('format {drive} [{size}]')
        .format(drive=user['drive']['name'], size=user['drive']['size']))

    cmd_args = shlex.split('wipefs -f -a {drive}'
                           .format(drive=user['drive']['name']))

    cmd = Popen(cmd_args, stdin=PIPE, stdout=PIPE)

    cmd = 'dd if=/dev/zero of={drive} bs=512 count=1 conv=notrunc'.format(
        drive=quote(user['drive']['name']))

    cmd = command_output(cmd)
    time.sleep(1)

    # Create new partition table
    logging.info(trad('create new {table} partition table on {drive}')
                 .format(table=user['drive']['table'].upper(),
                         drive=user['drive']['name']))

    cmd_args1 = Popen(['/usr/bin/printf', 'label: {table}'.format(
        table=user['drive']['table'])], stdout=PIPE)

    cmd_args2 = Popen(shlex.split('sfdisk -f -q --wipe=always {drive}'
                                  .format(drive=user['drive']['name'])),
                      stdin=cmd_args1.stdout, stdout=PIPE)

    cmd = cmd_args2.communicate()[0]
    time.sleep(1)

    # Create DOS partitions :
    #########################
    for partition, size in \
            zip(user['partitions']['name'], user['partitions']['size']):

        logging.info(
            trad('create {partition} partition [{size}] on {drive}')
            .format(partition=partition, size=size,
                    drive=user['drive']['name']))

        if size == 'freespace' or \
                ((user['drive']['lvm'] is True) and (partition == 'root')):
            size = '16T'

        size = parse_size(size.replace(',', '.'))
        size = round_number(size / 1000)

        cmd_args1 = Popen(['/usr/bin/printf', 'size={size}K'
                           .format(size=size)], stdout=PIPE)

        cmd_args2 = Popen(shlex.split('sfdisk -f -q --no-reread \
--wipe-partitions=always --append {d}'.format(d=user['drive']['name'])),
                          stdin=cmd_args1.stdout, stdout=PIPE)

        cmd = cmd_args2.communicate()[0]
        time.sleep(1)

    # Get ID and UUID of created partitions
    partition_drive_id()
    partition_uuid()

    # Set the partition types :
    ###########################
    for partition, drive_id in \
            zip(user['partitions']['name'], user['partitions']['drive_id']):

        if (user['firmware']['type'] == 'uefi') and (partition == 'boot'):
            gdisk_cmd = 't\nef00\nw'

            logging.info(
                trad('set EFI partition type for boot partition [{id}]')
                .format(id=drive_id))

        elif ((user['drive']['lvm'] is True) and (partition == 'root')):
            gdisk_cmd = 't\n1\n8e00\nw'

            logging.info(
                trad('set LVM partition type for root partition [{id}]')
                .format(id=drive_id))

        if 'gdisk_cmd' in locals():
            cmd_args1 = Popen(['/usr/bin/printf', gdisk_cmd], stdout=PIPE)
            cmd_args2 = Popen(shlex.split('gdisk {drive}'
                                          .format(
                                              drive=user['drive']['name'])),
                              stdin=cmd_args1.stdout, stdout=PIPE)

            cmd = cmd_args2.communicate()[0]

        time.sleep(1)

    # Logical Volume Manager :
    ##########################
    for partition, drive_id, size in \
            zip(user['partitions']['name'],
                user['partitions']['drive_id'],
                user['partitions']['size']):

        # Create LVM Volume on root partition
        if (user['drive']['lvm'] is True) and (partition == 'root'):

            # LVM on LUKS commands
            if user['drive']['luks'] is True:

                logging.info(trad('create LVM on LUKS [{id}]')
                             .format(id=drive_id))

                cmd_list = [
                    'cryptsetup luksFormat {id}'.format(id=drive_id),
                    'cryptsetup open {id} cryptlvm'.format(id=drive_id),
                    'pvcreate -y /dev/mapper/cryptlvm',
                    'vgcreate -y lvm /dev/mapper/cryptlvm']

            # LVM without LUKS commands
            else:
                logging.info(trad('create LVM Volume on [{id}]')
                             .format(id=drive_id))

                cmd_list = ['pvcreate -y {id}'.format(id=drive_id),
                            'vgcreate -y lvm {id}'.format(id=drive_id)]

            # Create Volume
            for cmd in cmd_list:
                cmd = Popen(shlex.split(cmd), stdin=PIPE, stdout=PIPE)

        # Create LVM Logical partitions
        if (user['drive']['lvm'] is True) and (partition != 'boot'):

            logging.info(trad('create {partition} LVM partition [{size}]')
                         .format(partition=partition, size=size))

            if size == 'freespace':
                size = '-l 100%FREE'
            else:
                size = '-L {size}'.format(size=size)

            cmd = Popen(shlex.split('lvcreate -y {size} {id}'
                                    .format(size=size, id=drive_id)),
                        stdin=PIPE, stdout=PIPE)

        time.sleep(1)

    # Update ID and UUID of created partitions
    partition_drive_id()
    partition_uuid()

    # Format the partitions :
    #########################
    for partition, drive_id, size, filesystem in \
            zip(user['partitions']['name'],
                user['partitions']['drive_id'],
                user['partitions']['size'],
                user['partitions']['filesystem']):

        logging.info(
            trad('format {partition} partition [{filesystem}] [{size}]')
            .format(partition=partition, filesystem=filesystem, size=size))

        if filesystem == 'fat32':
            filesystem = 'fat -F32'

        if partition == 'swap':
            format_cmd = 'yes | mkswap {id}'.format(id=drive_id)
        else:
            format_cmd = 'yes | mkfs.{filesystem} {id}'.format(
                filesystem=filesystem, id=drive_id)

        try:
            cmd = command_output(format_cmd)

        except CalledProcessError as error:
            logging.error(error)
            sys.exit(1)


# Mount the partitions.
##############################################################################
for mountorder, partition, drive_id, mountpoint in \
        sorted(zip(user['partitions']['mountorder'],
                   user['partitions']['name'],
                   user['partitions']['drive_id'],
                   user['partitions']['mountpoint'])):

    logging.info(trad('mount {partition} partition [{id}] on {mountpoint}')
                 .format(partition=partition, mountpoint=mountpoint,
                         id=drive_id))

    if partition == 'swap':
        cmd = Popen(shlex.split('swapon {id}'.format(id=drive_id)),
                    stdin=PIPE, stdout=PIPE)
    else:
        if not os.path.exists(mountpoint):
            os.makedirs(mountpoint)

        cmd = Popen(shlex.split('mount {id} {mountpoint}'
                                .format(id=drive_id, mountpoint=mountpoint)),
                    stdin=PIPE, stdout=PIPE)
    time.sleep(1)


# Update dictionary to settings.json
##############################################################################
with open('{path}/json/settings.json'.format(path=os.getcwd()), 'w',
          encoding='utf-8') as settings:
    json.dump(user, settings, ensure_ascii=False, indent=4)


# PyArchboot - Python Arch Linux Installer by grm34 under Apache License 2.0
##############################################################################
