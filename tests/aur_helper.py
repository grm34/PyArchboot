# -*- coding: utf-8 -*-

"""Install AUR Helper tests."""

import re
import shlex
from shutil import copyfile, copytree, move, rmtree
from subprocess import PIPE, Popen

username = 'luna'
aur_helper = 'trizen'


def run_command(cmd):
    """Subprocess Popen."""
    process = Popen(shlex.split(cmd),
                    stdin=PIPE, stdout=PIPE, encoding='utf-8')
    while True:
        output = process.stdout.readline()
        if output:
            print(output.strip())
        else:
            break
    command_output = process.poll()
    return command_output


# Set root privilege without password
with open('/mnt/etc/sudoers', 'r') as sudo:
    sudo_list = list(sudo)

sudo = []
for line in sudo_list:
    line = re.sub(' +', ' ', line)
    line = line.replace(
        '{user} ALL=(ALL) ALL'.format(user=username),
        '{user} ALL=(ALL) NOPASSWD: ALL'.format(user=username))
    sudo.append(line)

with open('/mnt/etc/sudoers', 'w+') as file:
    for line in sudo:
        file.write(line)


# Clone the AUR Helper repository
cmd = 'arch-chroot /mnt \
sudo -u {user} git clone https://aur.archlinux.org/{aur}.git \
/home/{user}/{aur}'.format(user=username,
                           aur=aur_helper.lower())
run_command(cmd)


# Install the AUR Helper
with open('/root/aur.sh', 'w+') as file:
    for line in ['#!/bin/bash\n', 'arch-chroot /mnt /bin/bash <<EOF\n',
                 'cd /home/{user}/{aur}\n'.format(user=username,
                                                  aur=aur_helper),
                 'sudo -u luna makepkg --noconfirm --needed -sic\n',
                 'EOF\n']:
        file.write(line)

cmd_list = ['chmod +x /root/aur.sh', '/root/aur.sh', 'rm /root/aur.sh']
for cmd in cmd_list:
    run_command('aur.sh')


# Restore root privilege access
with open('/mnt/etc/sudoers', 'r') as sudo:
    sudo_list = list(sudo)

sudo = []
for line in sudo_list:
    line = re.sub(' +', ' ', line)
    line = line.replace(
        '{user} ALL=(ALL) NOPASSWD: ALL'.format(user=username),
        '{user} ALL=(ALL) ALL'.format(user=username))
    sudo.append(line)

with open('/mnt/etc/sudoers', 'w+') as file:
    for line in sudo:
        file.write(line)


# Remove AUR Helper repository folder
rmtree('/mnt/home/{user}/{aur}'
       .format(user=username, aur=aur_helper.lower()))
