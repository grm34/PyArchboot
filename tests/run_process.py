# -*- coding: utf-8 -*-
"""Run process tests."""
import shlex
from subprocess import PIPE, STDOUT, Popen


def run_command(cmd):
    """Subprocess check_output."""
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


print('test is running...')

cmd = 'arch-chroot /mnt pacman --noconfirm --needed -S gnome-calculator'
run_command(cmd)

print('test done.')
