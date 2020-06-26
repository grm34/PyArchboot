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

import re

from humanfriendly import format_size, parse_size
from inquirer.errors import ValidationError


def size_counter(user):
    """
    Calculate remaining available disk space.

    Arguments
    ---------
        user: "Dictionary containing user's answers"

    Modules
    -------
        humanfriendly: "Parse a human readable data libraries"

    Returns
    -------
        "Integer of the current disk space usage"
    """
    counter = 0
    size_list = ['boot_size', 'root_size', 'swap_size', 'home_size']

    for size in size_list:
        if (size in user) and (user[size] is not None):
            counter += parse_size(user[size].replace(',', '.'))

    return counter


def size_index(user):
    """
    Set the index of the current partition.

    Arguments
    ---------
        user: "Dictionary containing user's answers"

    Returns
    -------
        "Integer of the current partition index"
    """
    index = 0
    if 'swap_size' in user:
        index = 3
    elif 'root_size' in user:
        index = 2
    elif 'boot_size' in user:
        index = 1

    return index


def size_validator(self, user, response):
    """
    Match regex, current partition min/max size and remaining disk space.

    Arguments
    ---------
        user: "Dictionary containing user's answers"
        response: "String containing current answer"

    Modules
    -------
        re: "Regular expression matching operations"
        humanfriendly: "Parse human readable data libraries"
        inquirer.errors: "Common base class for all non-exit exceptions"

    Functions
    ---------
        `size_counter`: "Returns integer of the current disk space usage"
        `size_index`: "Returns integer of the current partition index"

    Raises
    ------
        ValidationError: "Display a short description with available formats"

    Returns
    -------
        boolean: True
    """
    name = ['boot', 'root', 'swap', 'home']
    min_size = ['100M', '5G', '1G', '4G']
    max_size = ['2G', '16T', '32G', '16T']
    eq_size = ['512M', '25G', '2G', '100G']
    valid_size = r'^[1-9]{1}[0-9]{0,2}((,|\.)[0-9]{1,2}){0,1}(M|G|T){1}$'
    msg_error = self.trad('Invalid size for {name}: {response} (e.q., {eq})')
    msg_status = self.trad(
        'Minimum [{min}] Maximum [{max}] Remaining [{free}]')
    error = '{msg} {status}'.format(msg=msg_error, status=msg_status)

    if (not re.match(valid_size, response)) or \
            ((size_counter(user) + parse_size(response.replace(',', '.'))) >
             parse_size(user['drive'].split()[1].replace(',', '.'))) or \
            (parse_size(response.replace(',', '.')) <
             parse_size(min_size[size_index(user)])) or \
            (parse_size(response.replace(',', '.')) >
             parse_size(max_size[size_index(user)])):

        raise ValidationError('', reason=error.format(
            name=name[size_index(user)],
            response=response,
            eq=eq_size[size_index(user)],
            min=min_size[size_index(user)],
            max=max_size[size_index(user)],
            free=format_size(
                parse_size(user['drive'].split()[1].replace(',', '.')) -
                size_counter(user))))

    return True


def timezone_validator(self, response):
    """
    Match timezone code in libraries/timezone.

    Arguments
    ---------
        response: "String containing current answer"

    Raises
    ------
        ValidationError: "Display a short description with available formats"

    Returns
    -------
        boolean: True
    """
    timezone_list = open('libraries/timezone').read()
    if ('{response}\n'.format(response=response) not in timezone_list) or \
            (response == ''):

        raise ValidationError('', reason=self.trad(
            'Invalid timezone: {response} (e.q., Europe/Paris)').format(
                response=response))

    return True


def language_validator(self, response):
    """
    Match language code in libraries/locale.

    Arguments
    ---------
        response: "String containing current answer"

    Raises
    ------
        ValidationError: Display a short description with available formats"

    Returns
    -------
        boolean: True
    """
    language_list = open('libraries/locale').read()
    if ('{response}\n'.format(response=response) not in language_list) or \
            (response == ''):

        raise ValidationError('', reason=self.trad(
            'Invalid language code: {response} (e.q., fr_FR)').format(
                response=response))

    return True


def hostname_validator(self, response):
    """
    Match UNIX hostname regex.

    Arguments
    ---------
        response: "String containing current answer"

    Raises
    ------
        ValidationError: "Display a short description with available formats"

    Returns
    -------
        boolean: True
    """
    if not re.match(r'^[a-zA-Z0-9][-a-zA-Z0-9_]{1,31}$', response):

        raise ValidationError('', reason=self.trad(
            'Invalid hostname: {response} (e.q., my-computer)').format(
                response=response))

    return True


def passwd_validator(self, response):
    """
    Match UNIX password regex.

    Arguments
    ---------
        response: "String containing current answer"

    Raises
    ------
        ValidationError: "Display a short description with available formats"

    Returns
    -------
        boolean: True
    """
    info = self.trad('Password should be at least')
    valid = self.trad('8 chars long with one letter and one digit !')
    message = '{info} {valid}'.format(info=info, valid=valid)
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[\S]{8,}$', response):
        raise ValidationError('', reason=message)

    return True


def username_validator(self, response):
    """
    Match UNIX username regex.

    Arguments
    ---------
        response: "String containing current answer"

    Raises
    ------
        ValidationError: "Display a short description with available formats"

    Returns
    -------
        boolean: True
    """
    if not re.match(r'^[a-z_]{1}[a-z0-9_-]{1,31}$', response):

        raise ValidationError('', reason=self.trad(
            'Invalid username: {response} (e.q., JohnDoe)').format(
                response=response))

    return True


# PyArchboot - Python Arch Linux Installer by grm34 under Apache License 2.0
##############################################################################
