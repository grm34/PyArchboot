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


def partition_list_updater(self, user):
    """Delete previous partition to display an updated array after selection.

    Arguments:
        user -- Dictionary containing user's answers

    Returns:
        partition_list -- Array of the remaining partitions
    """
    for partition in ['boot_id', 'root_id', 'swap_id']:
        if (partition in user) and \
                (user[partition] in self.partition_list):
            self.partition_list.remove(user[partition])

    return self.partition_list


def desktop_extra_assigner(self, user):
    """Assign the extra packages name of the selected desktop.

    Arguments:
        user -- Dictionary containing user's answers

    Returns:
        desktop_choice -- String containing the question for the desktop
                          environment extra packages
    """
    choice = ['Gnome extra',
              'KDE applications',
              'Deepin extra',
              'Mate extra',
              'XFCE goodies']

    desktop_choice = self.trad('Do you wish to install {extra}').format(
        extra=choice[user['desktop']])

    return desktop_choice


# PyArchboot - Python Arch Linux Installer by grm34 under Apache License 2.0
##############################################################################
