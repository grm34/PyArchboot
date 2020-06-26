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
import re
from shlex import quote
from shutil import copy2, copyfile, copytree, move, rmtree

from .system_manager.unix_command import command_output, run_command


def set_mirrorlist(self):
    """
    Update pacman mirrorlist.

    Modules
    -------
        logging: "Event logging system for applications and libraries"

    Actions
    -------
        "Write {mirrorlist}:" /etc/pacman.d/mirrorlist
    """
    if self.user['mirrorlist'] is False:
        logging.info(self.trad('update mirrorlist'))

        with open('/etc/pacman.d/mirrorlist', 'w+') as mirrorlist:
            mirrorlist.write('{mirrors}'.format(
                mirrors=self.user['mirrorlist']))


def install_base_system(self):
    """
    Install Arch Linux base system.

    Modules
    -------
        logging: "Event logging system for applications and libraries"

    Submodules
    ----------
        `run_command`: "Subprocess Popen with console output"

    Actions:
    --------
        pacstrap /mnt {base}
    """
    logging.info(self.trad('install Arch Linux base system'))
    self.packages['base'] += ' {kernel}'.format(kernel=self.user['kernel'])

    if self.user['firmware']['driver'] is not None:
        self.packages['base'] += ' {fw}'.format(fw=self.packages['firmware'])

    if self.user['aur_helper'] is not None:
        self.packages['base'] += ' {dev}'.format(dev=self.packages['devel'])

    cmd = 'pacstrap /mnt {packages}'.format(packages=self.packages['base'])
    run_command(cmd)


def create_fstab(self):
    """
    Generate Filsystem Table.

    Modules
    -------
        logging: "Event logging system for applications and libraries"

    Submodules
    ----------
        `command_output`: "Subprocess check_output with return codes"
        `run_command`: "Subprocess Popen with console output"

    Actions
    -------
        genfstab -U -p /mnt >> /mnt/etc/fstab
    """
    logging.info(self.trad('create file system table'))
    cmd = 'genfstab -U -p /mnt >> /mnt/etc/fstab'
    command_output(cmd)
    cmd = 'cat /mnt/etc/fstab'
    run_command(cmd)


def set_timezone(self):
    """
    Set the user's time zone.

    Modules
    -------
        logging: "Event logging system for applications and libraries"

    Submodules
    ----------
        `run_command`: "Subprocess Popen with console output"

    Actions
    -------
        ln -sfv /usr/share/zoneinfo/{timezone} /mnt/etc/localtime
        hwclock "--systohc"
    """
    logging.info(self.trad('set timezone [{timezone}]')
                 .format(timezone=self.user['timezone']))

    cmd_list = ['ln -sfv /usr/share/zoneinfo/{timezone} /mnt/etc/localtime'
                .format(timezone=self.user['timezone']), 'hwclock --systohc']

    for cmd in cmd_list:
        run_command(cmd)


def set_locales(self):
    """
    Generate the user's locales.

    Submodules
    ----------
        `run_command`: "Subprocess Popen with console output"

    Actions
    -------
        arch-chroot /mnt locale-gen
        "Write {language}:" /mnt/etc/locale.conf
    """
    logging.info(self.trad('set locale [{locale}]')
                 .format(locale=self.user['language']))

    with open('/mnt/etc/locale.gen', 'a') as locale:
        locale.write('{language}.UTF-8 UTF-8\n'
                     .format(language=self.user['language']))

    cmd = 'arch-chroot /mnt locale-gen'
    run_command(cmd)

    with open('/mnt/etc/locale.conf', 'w+') as locale:
        locale.write(
            'LANG={language}.UTF-8\n'.format(language=self.user['language']))


def set_virtual_console(self):
    """
    Set the user's virtual console file.

    Modules
    -------
        logging: "Event logging system for applications and libraries"

    Actions
    -------
        "Write {keymap}:" /mnt/etc/vconsole.conf
    """
    logging.info(self.trad('set virtual console [{keymap}]')
                 .format(keymap=self.user['keymap']))

    with open('/mnt/etc/vconsole.conf', 'w+') as vconsole:
        vconsole.write('KEYMAP={keymap}\n'.format(keymap=self.user['keymap']))


def set_hostname_file(self):
    """
    Set the user's hostname file.

    Modules
    -------
        logging: "Event logging system for applications and libraries"

    Actions
    -------
        "Write {hostname}:" /mnt/etc/locale.conf
    """
    logging.info(self.trad('set hostname [{hostname}]')
                 .format(hostname=self.user['hostname']))

    with open('/mnt/etc/hostname', 'w+') as hostname:
        hostname.write('{hostname}\n'.format(hostname=self.user['hostname']))


def set_root_passwd(self):
    """
    Set the password for root.

    Modules
    -------
        logging: "Event logging system for applications and libraries"

    Submodules
    ----------
        `command_output`: "Subprocess Popen with return codes"

    Actions
    -------
        echo root:{passwd} | arch-chroot /mnt chpasswd -e
    """
    logging.info(self.trad('set root password'))
    cmd = 'echo root:{passwd} | arch-chroot /mnt chpasswd -e'.format(
        passwd=quote(self.user['passwords']['root']))

    command_output(cmd)


def create_user(self):
    """
    Create new user.

    Modules
    -------
        logging: "Event logging system for applications and libraries"
        shlex.quote: "Return a shell-escaped version of the string"

    Submodules
    ----------
        `run_command`: "Subprocess Popen with console output"
        `command_output`: "Subprocess Popen with return codes"

    Actions
    -------
        arch-chroot /mnt useradd -g users -m -s /bin/bash {user}
        echo {user}:{passwd} | arch-chroot /mnt chpasswd -e
    """
    logging.info(self.trad('create user {user}')
                 .format(user=self.user['username']))

    cmd = 'arch-chroot /mnt useradd -g users -m -s /bin/bash {user}'.format(
        user=self.user['username'])

    run_command(cmd)

    logging.info(self.trad('set password for user {user}')
                 .format(user=self.user['username']))

    cmd = 'echo {user}:{passwd} | arch-chroot /mnt chpasswd -e'.format(
        user=quote(self.user['username']),
        passwd=quote(self.user['passwords']['user']))

    command_output(cmd)


def install_network(self):
    """
    Install the network.

    Modules
    -------
        logging: "Event logging system for applications and libraries"

    Submodules
    ----------
        `run_command`: "Subprocess Popen with console output"

    Actions
    -------
        arch-chroot /mnt pacman "--noconfirm --needed" -S {network}
        arch-chroot /mnt systemctl enable NetworkManager
    """
    logging.info(self.trad('install network'))
    cmd_list = [
        'arch-chroot /mnt pacman --noconfirm --needed -S {net}'.format(
            net=self.packages['network']),
        'arch-chroot /mnt systemctl enable NetworkManager']

    for cmd in cmd_list:
        run_command(cmd)


def install_grub_bootloader(self):
    """
    Install grub bootloader.

    Modules
    -------
        logging: "Event logging system for applications and libraries"

    Submodules
    ----------
        `run_command`: "Subprocess Popen with console output"

    Actions
    -------
        arch-chroot /mnt pacman "--noconfirm --needed" -S {grub}
    """
    if (self.firmware == 'bios') or \
            ((self.firmware == 'uefi') and (self.efi == 'x86')):

        if self.user['ntfs'] is not False:
            self.packages['grub']['packages'] += ' {extras}'.format(
                extras=self.packages['grub']['extras'])

        logging.info(self.trad('install grub bootloader'))
        cmd = 'arch-chroot /mnt pacman --noconfirm --needed -S {grub}'.format(
            grub=self.packages['grub']['packages'])

        run_command(cmd)


def install_optional_packages(self):
    """
    Install optional packages.

    Submodules
    ----------
        `run_command`: "Subprocess Popen with console output"

    Actions
    -------
        arch-chroot /mnt pacman "--noconfirm --needed" -S {optional}
    """
    for choice, name in zip(
            [self.user['cpu']['microcode'],
             self.user['drive']['lvm'],
             self.user['ntfs'],
             self.user['gpu']['driver'],
             self.user['gpu']['hardvideo'],
             self.user['desktop_environment']['requirements'],
             self.user['desktop_environment']['packages'],
             self.user['display_manager']['packages']],
            ['microcode updates',
             'lvm support',
             'ntfs support',
             'GPU driver',
             'hardware video acceleration',
             'X window system',
             '{desktop}'.format(
                 desktop=self.user['desktop_environment']['name']),
             '{display}'.format(
                 display=self.user['display_manager']['name'])]):

        if (choice is not None) and (choice is not False):

            logging.info(self.trad('install {name}').format(name=name))
            chroot = 'arch-chroot /mnt'
            cmd = 'pacman --noconfirm --needed -S {opt}'.format(opt=choice)
            cmd = '{chroot} {cmd}'.format(chroot=chroot, cmd=cmd)
            run_command(cmd)


def configure_systemdboot(self):
    """
    Configure systemd-boot bootloader.

    Modules
    -------
        logging: "Event logging system for applications and libraries"
        shutil: "File and manipulation libraries"
        re: "Regular expression matching operations"

    Submodules
    ----------
        `run_command`: "Subprocess Popen with console output"

    Actions
    -------
        "Write {hooks}:" /mnt/etc/mkinitcpio.conf
        arch-chroot /mnt bootctl "--path=/boot" install
        "Write {loader}:" /mnt/boot/loader/loader.conf
        "Write {entry}:" /mnt/boot/loader/entries/arch.conf
        arch-chroot /mnt bootctl "--path=/boot" update
    """
    if (self.firmware == 'uefi') and (self.efi == 'x84'):
        logging.info(self.trad('configure systemd-boot bootloader'))

        # Update the HOOKS
        with open('/mnt/etc/mkinitcpio.conf', 'r') as mkinitcpio:
            mkinitcpio_list = list(mkinitcpio)

        move('/mnt/etc/mkinitcpio.conf',
             '/mnt/etc/mkinitcpio.backup',
             copy_function=copy2)

        mkinitcpio = []
        for line in mkinitcpio_list:
            line = re.sub(' +', ' ', line)

            if line.startswith('HOOKS=('):

                for key in [' keyboard', ' keymap', ' lvm2', ' encrypt']:
                    line = line.replace(key, '')

                line = line.replace(' filesystems',
                                    ' keyboard keymap lvm2 filesystems')

                if self.user['drive']['luks'] is not False:
                    line = line.replace(' filesystems', ' encrypt filesystems')

            mkinitcpio.append(line)

        with open('/mnt/etc/mkinitcpio.conf', 'w+') as file:
            for line in mkinitcpio:
                file.write(line)

        # Run bootctl install
        cmd = 'arch-chroot /mnt bootctl --path=/boot install'
        run_command(cmd)

        # Create loader.conf
        move('/mnt/boot/loader/loader.conf',
             '/mnt/boot/loader/loader.backup',
             copy_function=copy2)

        copyfile('config/loader.conf', '/mnt/boot/loader/loader.conf')

        # Create new boot entry
        systemdboot = ['title Arch Linux',
                       'linux /vmlinuz-{kernel}'.format(
                           kernel=self.user['kernel']),
                       'initrd /initramfs-{kernel}.img'.format(
                           kernel=self.user['kernel'])]

        if self.user['cpu']['microcode'] is not None:
            systemdboot.insert(2, 'initrd /{microcode}.img'.format(
                microcode=self.user['cpu']['microcode']))

        if self.user['drive']['luks'] is not False:
            opt = 'options cryptdevice=PARTUUID={uuid}:cryptlvm'.format(
                uuid=self.user['partitions']['partuuid'][1])

            arg = 'root=/dev/lvm/root quiet rw'
            options = '{opt} {arg}'.format(opt=opt, arg=arg)

        else:
            options = 'options root=PARTUUID={uuid} quiet rw'.format(
                uuid=self.user['partitions']['partuuid'][1])

        systemdboot.append(options)
        with open('/mnt/boot/loader/entries/arch.conf', 'w+') as file:
            for line in systemdboot:
                file.write(systemdboot)

        # Run bootctl update
        cmd = 'arch-chroot /mnt bootctl --path=/boot update'
        run_command(cmd)


def configure_grub(self):
    """
    Configure grub bootlader.

    Modules
    -------
        logging: "Event logging system for applications and libraries"
        shutil: "High-level file operations"
        re: "Regular expression matching operations"

    Submodules
    ----------
        `run_command`: "Subprocess Popen with console output"

    Actions
    -------
        arch-chroot /mnt grub-install "--target=i386-pc" {boot}
        "Copy Grub2-themes/Archlinux:" /mnt/boot/grub/themes/Archlinux
        "Write {config}:" /mnt/etc/default/grub
        arch-chroot /mnt grub-mkconfig -o /boot/grub/grub.cfg
    """
    if (self.firmware == 'bios') or \
            ((self.firmware == 'uefi') and (self.efi == 'x86')):
        logging.info(self.trad('configure grub bootloader'))

        # Run grub-install
        cmd = 'arch-chroot /mnt grub-install --target=i386-pc {boot}'.format(
            boot=self.user['drive']['boot'])

        run_command(cmd)

        # Add grub theme (Archlinux)
        copytree('libraries/grub2-themes/Archlinux',
                 '/mnt/boot/grub/themes/Archlinux',
                 copy_function=copy2)

        with open('/mnt/etc/default/grub', 'r') as grub:
            grub_list = list(grub)

        move('/mnt/etc/default/grub',
             '/mnt/etc/default/grub.backup',
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


def configure_desktop_environment(self):
    """
    Configure the desktop environment.

    Modules
    -------
        logging: "Event logging system for applications and libraries"
        shutil: "High-level file operations"
        re: "Regular expression matching operations"

    Submodules
    ----------
        `run_command`: "Subprocess Popen with console output"

    Actions
    -------
        "Write {keyboard}:" /mnt/etc/X11/xorg.conf.d/00-keyboard.conf
        "Write {xinitrc}:" /home/{user}/.xinitrc
        arch-chroot /mnt chmod 770 /home/{user}/.xinitrc
    """
    if self.user['desktop_environment']['name'] is not None:
        logging.info(self.trad('configure {desktop}').format(
            desktop=self.user['desktop_environment']['name']))

        # Set the keyboard layout
        with open('config/00-keyboard.conf', 'r') as keyboard:
            keyboard_list = list(keyboard)

        keyboard = []
        for line in keyboard_list:
            line = re.sub(' +', ' ', line)
            line = line.replace('keymap_code', self.user['keymap'])
            keyboard.append(line)

        with open('/mnt/etc/X11/xorg.conf.d/00-keyboard.conf', 'w+') as file:
            for line in keyboard:
                file.write(line)

        # Create xinitrc file (window managers only)
        if 'xorg-xinit' in self.user['desktop_environment']['requirements']:

            move('config/xinitrc.conf',
                 '/mnt/home/{user}/.xinitrc'
                 .format(user=self.user['username']),
                 copy_function=copy2)

            with open('/mnt/home/{user}/.xinitrc'
                      .format(user=self.user['username']),
                      'a') as xinitrc:

                xinitrc.write('exec {w}\n'.format(
                    w=self.user['desktop_environment']['name'].split(' ')[0]))

            cmd = 'arch-chroot /mnt chmod 770 /mnt/home/{x}/.xinitrc'.format(
                x=self.user['username'])

            run_command(cmd)


def configure_display_manager(self):
    """
    Configure the display manager.

    Modules
    -------
        logging: "Event logging system for applications and libraries"

    Submodules
    ----------
        `run_command`: "Subprocess Popen with console output"

    Actions
    -------
        arch-chroot /mnt systemctl enable {manager}

    """
    if self.user['display_manager']['name'] is not None:
        logging.info(self.trad('configure {dm}')
                     .format(dm=self.user['display_manager']['name']))

        # Enable display manager service
        if 'xdm' in self.user['display_manager']['name'].lower():
            service = 'xdm-archlinux'
        else:
            service = self.user['display_manager']['name'].lower().split()[0]

        cmd = 'arch-chroot /mnt systemctl enable {dm}'.format(dm=service)
        run_command(cmd)


def configure_gdm(self):
    """
    Confgure GDM display manager.

    Modules
    -------
        shutil: "High-level file operations"

    Actions
    -------
        "Write {xprofile}:" /mnt/etc/xprofile
    """
    if self.user['display_manager']['name'] is not None and \
            'gdm' in self.user['display_manager']['name'].lower():

        copyfile('config/xprofile.conf', '/mnt/etc/xprofile')


def configure_lightdm(self):
    """
    Confgure LightDM display manager.

    Modules
    -------
        shutil: "High-level file operations"
        re: "Regular expression matching operations"

    Actions
    -------
        "Write {conf}:" /mnt/etc/lightdm/lightdm.conf
    """
    if self.user['display_manager']['name'] is not None and \
            'lightdm' in self.user['display_manager']['name'].lower():

        with open('/mnt/etc/lightdm/lightdm.conf', 'r') as lightdm:
            lightdm_list = list(lightdm)

        move('/mnt/etc/lightdm/lightdm.conf',
             '/mnt/etc/lightdm/lightdm.backup',
             copy_function=copy2)

        lightdm = []
        for line in lightdm_list:
            session = 'greeter-session={dm}'.format(
                dm=self.user['display_manager']['session'])
            line = re.sub(' +', ' ', line)
            line = line.replace('#greeter-session=example-gtk-gnome', session)
            line = line.replace(
                '#greeter-setup-script=',
                'greeter-setup-script=/usr/bin/numlockx on')
            lightdm.append(line)

        with open('/mnt/etc/lightdm/lightdm.conf', 'w+') as file:
            for line in lightdm:
                file.write(line)


def configure_sddm(self):
    """
    Confgure SDDM display manager.

    Modules
    -------
        re: "Regular expression matching operations"

    Submodules
    ----------
        `command_output`: "Subprocess Popen with return codes"

    Actions
    -------
        arch-chroot /mnt sddm "--example-config" > /etc/sddm.backup
        "Write {conf}:" /mnt/etc/sddm.conf
    """
    if self.user['display_manager']['name'] is not None and \
            'sddm' in self.user['display_manager']['name'].lower():

        cmd = 'arch-chroot /mnt sddm --example-config > /etc/sddm.backup'
        command_output(cmd)

        with open('/mnt/etc/sddm.backup', 'r') as sddm:
            sddm_list = list(sddm)

        sddm = []
        for line in sddm_list:
            line = re.sub(' +', ' ', line)
            line = line.replace(
                'Session=',
                'Session={session}'.format(
                    session=self.user['display_manager']['session']))
            line = line.replace('Numlock=none', 'Numlock=on')
            sddm.append(line)

        with open('/mnt/etc/sddm.conf', 'w+') as file:
            for line in sddm:
                file.write(line)


def configure_lxdm(self):
    """
    Confgure LXDM display manager.

    Modules
    -------
        shutil: "High-level file operations"
        re: "Regular expression matching operations"

    Actions
    -------
        "Write {conf}:" /mnt/etc/lxdm/lxdm.conf
    """
    if self.user['display_manager']['name'] is not None and \
            'lxdm' in self.user['display_manager']['name'].lower():

        with open('/mnt/etc/lxdm/lxdm.conf', 'r') as lxdm:
            lxdm_list = list(lxdm)

        move('/mnt/etc/lxdm/lxdm.conf',
             '/mnt/etc/lxdm/lxdm.backup',
             copy_function=copy2)

        lxdm = []
        for line in lxdm_list:
            line = re.sub(' +', ' ', line)
            line = line.replace(
                '# session=/usr/bin/startlxde',
                'session={session}'.format(
                    session=self.user['display_manager']['session']))
            line = line.replace('# numlock=0', 'numlock=1')
            line = line.replace('white=',
                                'white={user}'.format(
                                    user=self.user['username']))
            lxdm.append(line)

        with open('/mnt/etc/lxdm/lxdm.conf', 'w+') as file:
            for line in lxdm:
                file.write(line)


def configure_xdm(self):
    """
    Confgure XDM display manager.

    Submodules
    ----------
        `run_command`: "Subprocess Popen with console output"

    Actions
    -------
        "Write {conf}:" /home/{user}/.session
        arch-chroot /mnt chmod 770 /home/{user}/.session
    """
    if self.user['display_manager']['name'] is not None and \
            'xdm' in self.user['display_manager']['name'].lower():

        with open('/mnt/home/{user}/.session'
                  .format(user=self.user['username']),
                  'a') as xdm:
            xdm.write('{session}'.format(
                session=self.user['display_manager']['session']))

        cmd = 'arch-chroot /mnt chmod 770 /mnt/home/{x}/.session'.format(
            x=self.user['username'])

        run_command(cmd)


def set_user_privileges(self):
    """
    Set user's privileges.

    Modules
    -------
        logging: "Event logging system for applications and libraries"

    Submodules
    ----------
        `run_command`: "Subprocess Popen with console output"
        `command_output`: "Subprocess Popen with return codes"

    Actions
    -------
        "Write {privileges}:" /mnt/etc/sudoers
        arch-chroot /mnt pwck
        arch-chroot /mnt grpck
        arch-chroot /mnt gpasswd -a {user} {group}
    """
    if self.user['power'] is not False:

        # Grant the user in the sudoers file (root privilege)
        logging.info(self.trad('give root privilege to the user {user}')
                     .format(user=self.user['username']))

        with open('/mnt/etc/sudoers', 'a') as sudo:
            sudo.write(
                '\n## {user} privilege specification\n{user} ALL=(ALL) ALL'
                .format(user=self.user['username']))

        # Add the user to all groups
        logging.info(self.trad('add user {user} to all groups')
                     .format(user=self.user['username']))

        cmd_list = ['pwck', 'grpck']
        for cmd in cmd_list:
            cmd = 'arch-chroot /mnt {cmd}'.format(cmd=cmd)
            run_command(cmd)

        cmd = 'cut -d: -f1 /mnt/etc/group'
        group_list = command_output(cmd).split('\n')
        group_list = list(filter(None, group_list))

        for group in group_list:
            cmd = 'arch-chroot /mnt gpasswd -a {user} {group}'.format(
                user=self.user['username'], group=group)
            run_command(cmd)


def install_aur_helper(self):
    """
    Install AUR Helper.

    Modules
    -------
        logging: "Event logging system for applications and libraries"
        shutil: "High-level file operations"
        re: "Regular expression matching operations"

    Submodules
    ----------
        `run_command`: "Subprocess Popen with console output"

    Actions
    -------
        Temporarily grants user to run command without password
        Clones AUR Helper repository
        Creates and executes bash script to perform install
        Removes AUR Helper repository folder
    """
    if self.user['aur_helper'] is not None:
        logging.info(self.trad('install {aur} AUR Helper')
                     .format(aur=self.user['aur_helper']))

        # Set root privilege without password
        with open('/mnt/etc/sudoers', 'r') as sudo:
            sudo_list = list(sudo)

        sudo = []
        for line in sudo_list:
            line = re.sub(' +', ' ', line)
            line = line.replace(
                '{user} ALL=(ALL) ALL'.format(user=self.user['username']),
                '{user} ALL=(ALL) NOPASSWD: ALL'.format(
                    user=self.user['username']))
            sudo.append(line)

        with open('/mnt/etc/sudoers', 'w+') as file:
            for line in sudo:
                file.write(line)

        # Clone the AUR Helper repository
        chroot = 'arch-chroot /mnt'
        url = 'https://aur.archlinux.org/{aur}.git'.format(
            aur=self.user['aur_helper'].lower())
        cmd = '{x} sudo -u {user} git clone {url} /home/{user}/{aur}'.format(
            x=chroot,
            user=self.user['username'],
            url=url,
            aur=self.user['aur_helper'].lower())
        run_command(cmd)

        # Create bash script to perform install
        with open('aur.sh', 'w+') as file:
            for line in ['#!/bin/bash\n',
                         'arch-chroot /mnt /bin/bash <<EOF\n',
                         'cd /home/{user}/{aur}\n'.format(
                             user=self.user['username'],
                             aur=self.user['aur_helper'].lower()),
                         'sudo -u {user} makepkg --noconfirm --needed -sic\n'
                         .format(user=self.user['username']),
                         'EOF\n']:
                file.write(line)

        # Install the AUR Helper
        cmd_list = ['chmod +x aur.sh', 'sh aur.sh', 'rm aur.sh']
        for cmd in cmd_list:
            run_command(cmd)

        # Restore root privilege access
        with open('/mnt/etc/sudoers', 'r') as sudo:
            sudo_list = list(sudo)

        sudo = []
        for line in sudo_list:
            line = re.sub(' +', ' ', line)
            line = line.replace(
                '{user} ALL=(ALL) NOPASSWD: ALL'.format(
                    user=self.user['username']),
                '{user} ALL=(ALL) ALL'.format(user=self.user['username']))
            sudo.append(line)

        with open('/mnt/etc/sudoers', 'w+') as file:
            for line in sudo:
                file.write(line)

        # Remove AUR Helper repository folder
        rmtree('/mnt/home/{user}/{aur}'
               .format(user=self.user['username'],
                       aur=self.user['aur_helper'].lower()))


def clean_pacman_cache(self):
    """
    Clean pacman cache and remove unused dependencies.

    Modules
    -------
        logging: "Event logging system for applications and libraries"
        shutil: "High-level file operations"
        re: "Regular expression matching operations"

    Submodules
    ----------
        `run_command`: "Subprocess Popen with console output"
        `command_output`: "Subprocess check_output with return codes"

    Actions
    -------
        arch-chroot /mnt pacman -Qdtd
        arch-chroot /mnt pacman "--noconfirm" -Rcsn {dependency}
        arch-chroot /mnt pacman "--noconfirm" -Sc
    """
    logging.info(
        self.trad('clean pacman cache and delete unused dependencies'))

    cmd = 'arch-chroot /mnt pacman -Qdtd'
    output = command_output(cmd)

    if (output is not False) or (output is not None) or (output != ''):
        output = list(filter(None, output.split('\n')))

        for dependency in output:
            cmd = 'arch-chroot /mnt pacman --noconfirm -Rcsn {dep}'.format(
                dep=dependency)
            run_command(cmd)

    cmd = 'arch-chroot /mnt pacman --noconfirm -Sc'
    run_command(cmd)


# PyArchboot - Python Arch Linux Installer by grm34 under Apache License 2.0
##############################################################################
