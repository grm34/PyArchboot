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

import os
import re

from humanfriendly import format_size, parse_size
from inquirer.errors import ValidationError

from . import settings

trad = settings.trad

def size_counter(user):
    """Calculate disk space usage."""
    counter = 0
    size_list = ['boot_size', 'root_size', 'swap_size', 'home_size']

    for size in size_list:
        if (size in user) and (user[size] is not None):
            counter += parse_size(user[size].replace(',', '.'))

    return counter


def index_counter(user):
    """Define partitions index."""
    index = 0
    if 'swap_size' in user:
        index = 3
    elif 'root_size' in user:
        index = 2
    elif 'boot_size' in user:
        index = 1

    return index


def size_validator(user, response):
    """Validate partition sizes."""
    name = ['boot', 'root', 'swap', 'home']
    min_size = ['100M', '5G', '1G', '4G']
    max_size = ['2G', '16T', '32G', '16T']
    eq_size = ['512M', '25G', '2G', '100G']
    valid_size = r'^[1-9]{1}[0-9]{0,2}((,|\.)[0-9]{1,2}){0,1}(M|G|T){1}$'

    if (not re.match(valid_size, response)) \
            or ((size_counter(user) + parse_size(response
                                                .replace(',', '.'))) >
                parse_size(user['drive'].split()[1].replace(',', '.'))) \
            or (parse_size(response.replace(',', '.')) <
                parse_size(min_size[index_counter(user)])) \
            or (parse_size(response.replace(',', '.')) >
                parse_size(max_size[index_counter(user)])):

        raise ValidationError('', reason=trad('Invalid size for {name}: \
{response} (e.q., {eq}) Minimum [{min}] Maximum [{max}] \
Remaining [{free}]'.format(
            name=name[index_counter(user)],
            response=response, eq=eq_size[index_counter(user)],
            min=min_size[index_counter(user)],
            max=max_size[index_counter(user)],
            free=format_size(
                parse_size(user['drive'].split()[1].replace(',', '.')) -
                size_counter(user)))))

    return True


def timezone_validator(user, response):
    """Match timezone code in libraries/timezone."""
    timezone_list = open(
        '{path}/libraries/timezone'.format(path=os.getcwd())).read()

    if ('{response}\n'.format(response=response) not in timezone_list) or \
            (response == ''):

        raise ValidationError('', reason=trad(
            'Invalid timezone: {response} (e.q., Europe/Paris)'.format(
                response=response)))

    return True


def language_validator(user, response):
    """Match language code in libraries/language."""
    language_list = open(
        '{path}/libraries/language'.format(path=os.getcwd())).read()

    if ('{response}\n'.format(response=response) not in language_list) or \
            (response == ''):

        raise ValidationError('', reason=trad(
            'Invalid language code: {response} (e.q., fr_FR)'
            .format(response=response)))

    return True


def hostname_validator(user, response):
    """Regex to match UNIX hostnames."""
    if not re.match(r'^[a-zA-Z0-9][-a-zA-Z0-9_]{1,31}$', response):

        raise ValidationError('', reason=trad(
            'Invalid hostname: {response} (e.q., my-computer)'
            .format(response=response)))

    return True


def passwd_validator(user, response):
    """Regex to match UNIX passwords."""
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[\S]{8,}$', response):

        raise ValidationError('', reason=trad(
            'Password should be at least 8 chars long with \
one letter and one digit !'))

    return True


def username_validator(user, response):
    """Regex to match UNIX usernames."""
    if not re.match(r'^[a-z_]{1}[a-z0-9_-]{1,31}$', response):

        raise ValidationError('', reason=trad(
            'Invalid username: {response} (e.q., JohnDoe)'
            .format(response=response)))

    return True


# PyArchboot - Python Arch Linux Installer by grm34 under Apache License 2.0
##############################################################################
