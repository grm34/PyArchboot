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


def ignore_lvm(user):
    """Ignore LVM support in case of BIOS Firmware."""
    if user['drive'] is None:
        return True


def ignore_luks(user):
    """Ignore LUKS support in case of BIOS Firmware."""
    if user['lvm'] is False:
        return True


def ignore_boot_size(user):
    """Ignore boot partition size in case of custom partitions mode."""
    if user['drive'] is None:
        return True


def ignore_root_freespace(user):
    """Ignore freespace for root when optional partitions used."""
    if (user['drive'] is None) or ('Home' in user['optional_partitions']):
        return True


def ignore_root_size(user):
    """Ignore root partition size in case of freespace or custom mode."""
    if (user['drive'] is None) or (user['root_freespace'] is True):
        return True


def ignore_swap_size(user):
    """Ignore swap partition size in case of None or custom mode."""
    if (user['drive'] is None) \
            or ('Swap' not in user['optional_partitions']):
        return True


def ignore_home_freespace(user):
    """Ignore freespace for home in case of None or custom mode."""
    if (user['drive'] is None) \
            or ('Home' not in user['optional_partitions']):
        return True


def ignore_home_size(user):
    """Ignore home partition size in case of None or custom mode."""
    if (user['drive'] is None) or \
            ('Home' not in user['optional_partitions']) or \
            (user['home_freespace'] is True):
        return True


def ignore_required_partition_id(user):
    """Ignore partition selection if dedicated drive or no partition."""
    if (user['drive'] is not None) or (partition_list is None):
        return True


def ignore_swap_id(user):
    """Ignore swap partition selection in case of dedicated drive."""
    if (user['drive'] is not None) or \
            ('Swap' not in user['optional_partitions']):
        return True


def ignore_home_id(user):
    """Ignore home partition selection in case of dedicated drive."""
    if (user['drive'] is not None) or \
            ('Home' not in user['optional_partitions']):
        return True


def ignore_timezone(user):
    """Ignore custom timezone in case of detected one selected."""
    if user['timezone'] is not None:
        return True


def ignore_desktop_extra(user):
    """Ignore desktop extras when DE is None or no extra packages."""
    if (user['desktop'] is None) or \
            (user['desktop'] not in [0, 1, 2, 3, 4]):
        return True


def ignore_display_manager(user):
    """Ignore display manager selection in case of DE is None."""
    if user['desktop'] is None:
        return True


def ignore_lightdm_greeter(user):
    """Ignore LightDM greeter when display manager is not LightDM."""
    if (user['desktop'] is None) or (user['display'] != 1):
        return True


def ignore_gpu_driver(user):
    """Ignore GPU driver choice when DE is None or no controller."""
    if (user['desktop'] is None) or (gpu_list == ['']) \
            or (gpu_list is False):
        return True


def ignore_vga(user):
    """Ignore VGA Controller selection in case of GPU driver is False."""
    if user['gpu_driver'] is False:
        return True


def ignore_nvidia_proprietary(user):
    """Ignore proprietary drivers if no GPU or GPU is not nVidia."""
    if (user['gpu_driver'] is False) or \
            ('nvidia' not in user['vga_controller']):
        return True


# PyArchboot - Python Arch Linux Installer by grm34 under Apache License 2.0
##############################################################################
