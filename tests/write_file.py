# -*- coding: utf-8 -*-

import re

print('test is running...')

with open('config/00-keyboard.conf', 'r') as keyboard:
    keyboard_list = list(keyboard)

keyboard = []
for line in keyboard_list:
    line = re.sub(' +', ' ', line)
    line = line.replace('keymap_code', 'fr')
    keyboard.append(line)

with open('00-keyboard.conf', 'w+') as file:
    for line in keyboard:
        file.write(line)

print('test done.')
