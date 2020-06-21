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
import re
import shlex
import sys
from shlex import quote
from shutil import copy2, copyfile, copytree, move, rmtree
from subprocess import (PIPE, CalledProcessError, Popen, SubprocessError,
                        check_output)

# Load app settings
with open('{path}/json/app.json'.format(path=os.getcwd()), 'r',
          encoding='utf-8') as app_settings:
    app = json.load(app_settings)

# Load user settings
with open('{path}/json/settings.json'.format(path=os.getcwd()), 'r',
          encoding='utf-8') as settings:
    user = json.load(settings)

# Load archlinux packages
with open('{path}/json/packages.json'.format(path=os.getcwd()), 'r',
          encoding='utf-8') as packages_json:
    packages = json.load(packages_json)

# Load app language
language = gettext.translation('PyArchboot', localedir='locales',
                               languages=['{lang}'.format(lang=app['lang'])])
trad = language.gettext


# Python subprocess commands.
##############################################################################


def run_command(cmd):
    """Subprocess Popen with console output.

    Arguments:
        cmd {list} -- UNIX command (shlex splitted string)
    """
    try:
        process = Popen(shlex.split(cmd),
                        stdin=PIPE, stdout=PIPE, encoding='utf-8')

    except (SubprocessError, OSError, ValueError) as error:
        logging.error(error)
        sys.exit(1)

    while True:
        output = process.stdout.readline()
        if output:
            logging.debug(output.strip())
            print(output.strip())
        else:
            break

    output = process.poll()
    return output


def command_output(cmd):
    """Get the output of an UNIX command.

    Arguments:
        cmd {string} -- quoted UNIX command
    """
    try:
        output = check_output(cmd, shell=False, encoding='utf-8')

    except CalledProcessError as error:
        logging.error(error)
        sys.exit(1)

    return output


# Install Arch Linux base system.
##############################################################################

# Configure the mirrors
if user['mirrorlist'] is False:
    logging.info(trad('update mirrorlist'))

    with open('/etc/pacman.d/mirrorlist', 'w+') as mirrorlist:
        mirrorlist.write('{mirrors}'.format(mirrors=user['mirrorlist']))


# Install essential packages
logging.info(trad('install Arch Linux base system'))

packages['base'] += ' {kernel}'.format(kernel=user['kernel'])

if user['firmware']['driver'] is not None:
    packages['base'] += ' {fw}'.format(fw=packages['firmware'])

if user['aur_helper'] is not None:
    packages['base'] += ' {devel}'.format(devel=packages['devel'])

cmd = 'pacstrap /mnt {packages}'.format(packages=packages['base'])
run_command(cmd)


# Generate FSTAB
logging.info(trad('create file system table'))

cmd = 'genfstab -U -p /mnt >> /mnt/etc/fstab'
command_output(cmd)

cmd = 'cat /mnt/etc/fstab'
run_command(cmd)


# Configure the timezone
logging.info(
    trad('set timezone [{timezone}]').format(timezone=user['timezone']))

cmd_list = ['ln -sfv /usr/share/zoneinfo/{timezone} /mnt/etc/localtime'
            .format(timezone=user['timezone']), 'hwclock --systohc']

for cmd in cmd_list:
    run_command(cmd)


# Set localization
logging.info(trad('set locale [{locale}]').format(locale=user['language']))

with open('/mnt/etc/locale.gen', 'a') as locale:
    locale.write('{language}.UTF-8 UTF-8\n'.format(language=user['language']))

cmd = 'arch-chroot /mnt locale-gen'
run_command(cmd)

with open('/mnt/etc/locale.conf', 'w+') as locale:
    locale.write('LANG={language}.UTF-8\n'.format(language=user['language']))


# Set the virtual console
logging.info(
    trad('set virtual console [{keymap}]').format(keymap=user['keymap']))

with open('/mnt/etc/vconsole.conf', 'w+') as vconsole:
    vconsole.write('KEYMAP={keymap}\n'.format(keymap=user['keymap']))


# Set the hostname file
logging.info(
    trad('set hostname [{hostname}]').format(hostname=user['hostname']))

with open('/mnt/etc/hostname', 'w+') as hostname:
    hostname.write('{hostname}\n'.format(hostname=user['hostname']))


# Set the root password
logging.info(trad('set root password'))

cmd = 'echo root:{passwd} | arch-chroot /mnt chpasswd -e'.format(
    passwd=quote(user['passwords']['root']))

command_output(cmd)


# Create the user
logging.info(trad('create user {user}').format(user=user['username']))

cmd = 'arch-chroot /mnt useradd -g users -m -s /bin/bash {user}'.format(
    user=user['username'])

run_command(cmd)


# Set the user password
logging.info(
    trad('set password for user {user}').format(user=user['username']))

cmd = 'echo {user}:{passwd} | arch-chroot /mnt chpasswd -e'.format(
    user=quote(user['username']), passwd=quote(user['passwords']['user']))

command_output(cmd)


# Install the network
logging.info(trad('install network'))

cmd_list = [
    'arch-chroot /mnt pacman --noconfirm --needed -S {net}'.format(
        net=packages['network']),
    'arch-chroot /mnt systemctl enable NetworkManager']

for cmd in cmd_list:
    run_command(cmd)


# Install the bootloader
if user['firmware']['type'] == 'bios':

    if user['ntfs'] is not False:
        packages['grub']['packages'] += ' {extras}'.format(
            extras=packages['grub']['extras'])

    logging.info(trad('install grub bootloader'))

    cmd = 'arch-chroot /mnt pacman --noconfirm --needed -S {grub}'.format(
        grub=packages['grub']['packages'])

    run_command(cmd)


# Install optional packages
for choice, name in zip(
    [user['cpu']['microcode'], user['drive']['lvm'], user['ntfs'],
     user['gpu']['driver'], user['gpu']['hardvideo'],
     user['desktop_environment']['requirements'],
     user['desktop_environment']['packages'],
     user['display_manager']['packages']],
    ['microcode updates', 'lvm support', 'ntfs support',
     'GPU driver', 'hardware video acceleration', 'X window system',
     '{desktop}'.format(desktop=user['desktop_environment']['name']),
     '{display}'.format(display=user['display_manager']['name'])]):

    if (choice is not None) and (choice is not False):

        logging.info(trad('install {name}').format(name=name))

        cmd = 'arch-chroot /mnt pacman --noconfirm --needed -S {opt}'.format(
            opt=choice)

        run_command(cmd)


# Configure the bootloader.
##############################################################################

# Configure systemd-boot (UEFI)
if (user['firmware']['type'] == 'uefi') and \
        (user['firmware']['version'] == 'x64'):

    logging.info(trad('configure bootloader [systemd-boot]'))

    # Update the HOOKS
    with open('/mnt/etc/mkinitcpio.conf', 'r') as mkinitcpio:
        mkinitcpio_list = list(mkinitcpio)

    move('/mnt/etc/mkinitcpio.conf', '/mnt/etc/mkinitcpio.backup',
         copy_function=copy2)

    mkinitcpio = []
    for line in mkinitcpio_list:
        line = re.sub(' +', ' ', line)

        if line.startswith('HOOKS=('):

            for key in [' keyboard', ' keymap', ' lvm2', ' encrypt']:
                line = line.replace(key, '')

            line = line.replace(' filesystems',
                                ' keyboard keymap lvm2 filesystems')

            if user['drive']['luks'] is not False:
                line = line.replace(' filesystems', ' encrypt filesystems')

        mkinitcpio.append(line)

    with open('/mnt/etc/mkinitcpio.conf', 'w+') as file:
        for line in mkinitcpio:
            file.write(line)

    # Run bootctl install
    cmd = 'arch-chroot /mnt bootctl --path=/boot install'
    run_command(cmd)

    # Create loader.conf
    move('/mnt/boot/loader/loader.conf', '/mnt/boot/loader/loader.backup',
         copy_function=copy2)

    copyfile('config/loader.conf', '/mnt/boot/loader/loader.conf')

    # Create new boot entry
    systemdboot = ['title Arch Linux',
                   'linux /vmlinuz-{kernel}'.format(kernel=user['kernel']),
                   'initrd /initramfs-{kernel}.img'.format(
                       kernel=user['kernel'])]

    if user['cpu']['microcode'] is not None:
        systemdboot.insert(2, 'initrd /{microcode}.img'
                           .format(microcode=user['cpu']['microcode']))

    if user['drive']['luks'] is not False:
        systemdboot.append('options cryptdevice=PARTUUID={uuid}:cryptlvm \
root=/dev/lvm/root quiet rw'.format(uuid=user['partitions']['partuuid'][1]))

    else:
        systemdboot.append('options root=PARTUUID={uuid} quiet rw'
                           .format(uuid=user['partitions']['partuuid'][1]))

    with open('/mnt/boot/loader/entries/arch.conf', 'w+') as file:
        for line in systemdboot:
            file.write(systemdboot)

    # Run bootctl update
    cmd = 'arch-chroot /mnt bootctl --path=/boot update'
    run_command(cmd)


# Configure grub (BIOS)
else:
    logging.info(trad('configure bootloader [grub2]'))

    # Run grub-install
    cmd = 'arch-chroot /mnt grub-install --target=i386-pc {boot}'.format(
        boot=user['drive']['boot'])

    run_command(cmd)

    # Add grub theme (Archlinux)
    copytree('libraries/grub2-themes/Archlinux',
             '/mnt/boot/grub/themes/Archlinux', copy_function=copy2)

    with open('/mnt/etc/default/grub', 'r') as grub:
        grub_list = list(grub)

    move('/mnt/etc/default/grub', '/mnt/etc/default/grub.backup',
         copy_function=copy2)

    grub = []
    for line in grub_list:
        line = re.sub(' +', ' ', line)
        line = line.replace('GRUB_GFXMODE=auto', 'GRUB_GFXMODE=1024x768')
        line = line.replace(
            '#GRUB_THEME="/path/to/gfxtheme"',
            'GRUB_THEME="/boot/grub/themes/Archlinux/theme.txt"')

        grub.append(line)

    with open('/mnt/etc/default/grub', 'w+') as file:
        for line in grub:
            file.write(line)

    # Run grub-mkconfig
    cmd = 'arch-chroot /mnt grub-mkconfig -o /boot/grub/grub.cfg'
    run_command(cmd)


# Configure the desktop environment.
##############################################################################
if user['desktop_environment']['name'] is not None:
    logging.info(trad('configure {desktop}'
                      .format(desktop=user['desktop_environment']['name'])))

    # Set the keyboard layout
    with open('config/00-keyboard.conf', 'r') as keyboard:
        keyboard_list = list(keyboard)

    keyboard = []
    for line in keyboard_list:
        line = re.sub(' +', ' ', line)
        line = line.replace('keymap_code', user['keymap'])
        keyboard.append(line)

    with open('/mnt/etc/X11/xorg.conf.d/00-keyboard.conf', 'w+') as file:
        for line in keyboard:
            file.write(line)

    # Create xinitrc file (window managers only)
    if 'xorg-xinit' in user['desktop_environment']['requirements']:

        move('config/xinitrc.conf',
             '/mnt/home/{user}/.xinitrc'.format(user=user['username']),
             copy_function=copy2)

        with open('/mnt/home/{user}/.xinitrc'.format(user=user['username']),
                  'a') as xinitrc:

            xinitrc.write('exec {wm}\n'.format(
                wm=user['desktop_environment']['name'].split(' ')[0]))

        cmd = 'arch-chroot /mnt chmod 770 /mnt/home/{user}/.xinitrc'.format(
            user=user['username'])

        run_command(cmd)


# Configure the display manager.
##############################################################################
if user['display_manager']['name'] is not None:
    logging.info(trad('configure {dm}'
                      .format(dm=user['display_manager']['name'])))

    # Enable display manager service
    if user['display_manager']['name'].lower() == 'xdm display manager':
        service = 'xdm-archlinux'

    else:
        service = user['display_manager']['name'].lower().split()[0]

    cmd = 'arch-chroot /mnt systemctl enable {dm}'.format(dm=service)
    run_command(cmd)

    # Configure GDM
    if user['display_manager']['name'].lower() == 'gdm display manager':
        copyfile('config/xprofile.conf', '/mnt/etc/xprofile')

    # Configure LightDM
    elif user['display_manager']['name'].lower() == 'lightdm display manager':

        with open('/mnt/etc/lightdm/lightdm.conf', 'r') as lightdm:
            lightdm_list = list(lightdm)

        move('/mnt/etc/lightdm/lightdm.conf',
             '/mnt/etc/lightdm/lightdm.backup', copy_function=copy2)

        lightdm = []
        for line in lightdm_list:
            line = re.sub(' +', ' ', line)
            line = line.replace('#greeter-session=example-gtk-gnome',
                                'greeter-session={dm}'.format(
                                    dm=user['display_manager']['session']))
            line = line.replace('#greeter-setup-script=',
                                'greeter-setup-script=/usr/bin/numlockx on')
            lightdm.append(line)

        with open('/mnt/etc/lightdm/lightdm.conf', 'w+') as file:
            for line in lightdm:
                file.write(line)

    # Configure SDDM
    elif user['display_manager']['name'].lower() == 'sddm display manager':

        cmd = 'arch-chroot /mnt sddm --example-config > /etc/sddm.backup'
        command_output(cmd)

        with open('/mnt/etc/sddm.backup', 'r') as sddm:
            sddm_list = list(sddm)

        sddm = []
        for line in sddm_list:
            line = re.sub(' +', ' ', line)
            line = line.replace(
                'Session=', 'Session={session}'
                .format(session=user['display_manager']['session']))
            line = line.replace('Numlock=none', 'Numlock=on')
            sddm.append(line)

        with open('/mnt/etc/sddm.conf', 'w+') as file:
            for line in sddm:
                file.write(line)

    # Configure LXDM
    elif user['display_manager']['name'].lower() == 'lxdm display manager':

        with open('/mnt/etc/lxdm/lxdm.conf', 'r') as lxdm:
            lxdm_list = list(lxdm)

        move('/mnt/etc/lxdm/lxdm.conf', '/mnt/etc/lxdm/lxdm.backup',
             copy_function=copy2)

        lxdm = []
        for line in lxdm_list:
            line = re.sub(' +', ' ', line)
            line = line.replace(
                '# session=/usr/bin/startlxde', 'session={session}'
                .format(session=user['display_manager']['session']))
            line = line.replace('# numlock=0', 'numlock=1')
            line = line.replace('white=', 'white={user}'
                                .format(user=user['username']))
            lxdm.append(line)

        with open('/mnt/etc/lxdm/lxdm.conf', 'w+') as file:
            for line in lxdm:
                file.write(line)

    # Configure XDM
    elif user['display_manager']['name'].lower() == 'xdm display manager':

        with open('/mnt/home/{user}/.session'.format(user=user['username']),
                  'a') as xdm:
            xdm.write('{session}'.format(
                session=user['display_manager']['session']))

        cmd = 'arch-chroot /mnt chmod 770 /mnt/home/{user}/.session'.format(
            user=user['username'])

        run_command(cmd)


# Configure user privileges.
##############################################################################
if user['power'] is not False:

    # Grant the user in the sudoers file (root privilege)
    logging.info(trad('give root privilege to the user {user}'
                      .format(user=user['username'])))

    with open('/mnt/etc/sudoers', 'a') as sudo:
        sudo.write(
            '\n## {user} privilege specification\n{user} ALL=(ALL) ALL'
            .format(user=user['username']))

    # Add the user to all groups
    logging.info(
        trad('add user {user} to all groups'.format(user=user['username'])))

    cmd_list = ['pwck', 'grpck']
    for cmd in cmd_list:
        cmd = 'arch-chroot /mnt {cmd}'.format(cmd=cmd)
        run_command(cmd)

    cmd = 'cut -d: -f1 /mnt/etc/group'
    group_list = command_output(cmd).split('\n')
    group_list = list(filter(None, group_list))

    for group in group_list:
        cmd = 'arch-chroot /mnt gpasswd -a {user} {group}'.format(
            user=user['username'], group=group)

        run_command(cmd)


# Install the AUR Helper.
##############################################################################
if user['aur_helper'] is not None:
    logging.info(
        trad('install {aur} AUR Helper'.format(aur=user['aur_helper'])))

    # Set root privilege without password
    with open('/mnt/etc/sudoers', 'r') as sudo:
        sudo_list = list(sudo)

    sudo = []
    for line in sudo_list:
        line = re.sub(' +', ' ', line)
        line = line.replace(
            '{user} ALL=(ALL) ALL'.format(user=user['username']),
            '{user} ALL=(ALL) NOPASSWD: ALL'.format(user=user['username']))
        sudo.append(line)

    with open('/mnt/etc/sudoers', 'w+') as file:
        for line in sudo:
            file.write(line)

    # Clone the AUR Helper repository
    cmd = 'arch-chroot /mnt \
sudo -u {user} git clone https://aur.archlinux.org/{aur}.git \
/home/{user}/{aur}'.format(user=user['username'],
                           aur=user['aur_helper'].lower())
    run_command(cmd)

    # Install the AUR Helper
    with open('/root/aur.sh', 'w+') as file:
        for line in ['#!/bin/bash\n', 'arch-chroot /mnt /bin/bash <<EOF\n',
                     'cd /home/{user}/{aur}\n'.format(user=user['username'],
                                                      aur=user['aur_helper']),
                     'sudo -u luna makepkg --noconfirm --needed -sic\n',
                     'EOF\n']:
            file.write(line)

    cmd_list = ['chmod +x /root/aur.sh', '/root/aur.sh', 'rm /root/aur.sh']
    for cmd in cmd_list:
        run_command(cmd)

    # Restore root privilege access
    with open('/mnt/etc/sudoers', 'r') as sudo:
        sudo_list = list(sudo)

    sudo = []
    for line in sudo_list:
        line = re.sub(' +', ' ', line)
        line = line.replace(
            '{user} ALL=(ALL) NOPASSWD: ALL'.format(user=user['username']),
            '{user} ALL=(ALL) ALL'.format(user=user['username']))
        sudo.append(line)

    with open('/mnt/etc/sudoers', 'w+') as file:
        for line in sudo:
            file.write(line)

    # Remove AUR Helper repository folder
    rmtree('/mnt/home/{user}/{aur}'
           .format(user=user['username'], aur=user['aur_helper'].lower()))


# Remove unused dependencies and clean pacman cache.
##############################################################################
logging.info(trad('clean pacman cache and delete unused dependencies'))

cmd = 'arch-chroot /mnt pacman -Qdtd'
dependencies_list = command_output(cmd).split('\n')
dependencies_list = list(filter(None, dependencies_list))

if (dependencies_list != '') or (dependencies_list is not None):
    for dependency in dependencies_list:

        cmd = 'arch-chroot /mnt pacman --noconfirm -Rcsn {dep}'.format(
            dep=dependency)

        run_command(cmd)

cmd = 'arch-chroot /mnt pacman --noconfirm -Sc'
run_command(cmd)


# PyArchboot - Python Arch Linux Installer by grm34 under Apache License 2.0
##############################################################################
