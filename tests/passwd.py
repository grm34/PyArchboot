# -*- coding: utf-8 -*-
"""Store encrypted passwords tests."""
from crypt import METHOD_SHA512, crypt, mksalt
from shlex import quote
from subprocess import check_output

username = 'luna'
userpass = 'luna34jtm'
userpasswd = crypt(userpass, mksalt(METHOD_SHA512))

print('test is running...')

cmd = check_output('echo luna:{passwd} | arch-chroot /mnt chpasswd -e'
                   .format(user=quote(username),
                           passwd=quote(userpasswd)),
                   shell=False, encoding='utf-8')

print('test done.')
