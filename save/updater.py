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

from .system import get_settings

partition_list = get_settings.partition('updater')


def partition_list_updater(user):
    """Del selected partition to display an updated array after selection.

    Returns:
        partition_list {array} -- remaining partitions
    """
    if user['boot_id'] in partition_list:
        partition_list.remove(user['boot_id'])

    if 'root_id' in user:
        if user['root_id'] in partition_list:
            partition_list.remove(user['root_id'])

    if 'swap_id' in user:
        if user['swap_id'] in partition_list:
            partition_list.remove(user['swap_id'])

    return partition_list


def desktop_extra_updater(user):
    """Assign the extra packages name of the selected desktop.

    Returns:
        desktop_choice {string} -- question for desktop environment extra
    """
    choice = ['Gnome extra', 'KDE applications', 'Deepin extra',
              'Mate extra', 'XFCE goodies']

    desktop_choice = trad('Do you wish to install {extra}').format(
        extra=choice[user['desktop']])

    return desktop_choice


# PyArchboot - Python Arch Linux Installer by grm34 under Apache License 2.0
##############################################################################
