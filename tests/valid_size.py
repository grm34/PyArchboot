# -*- coding: utf-8 -*-
import re

import inquirer
from humanfriendly import format_size, parse_size
from inquirer import errors
from inquirer.themes import load_theme_from_dict


def size_counter(user):

    counter = 0
    size_list = ['boot_size', 'root_size', 'swap_size', 'home_size']

    for size in size_list:
        if (size in user) and (user[size] is not None):
            size = parse_size(user[size].replace(',', '.'))
        else:
            size = 0
        counter += size

    return counter


def index_counter(user):

    index = 0
    if 'swap_size' in user:
        index = 3
    elif 'root_size' in user:
        index = 2
    elif 'boot_size' in user:
        index = 1

    return index


def size_validation(user, response):

    drive = '465,4G'
    name = ['boot', 'root', 'swap', 'home']
    eq_size = ['512M', '25G', '2G', '100G']
    min_size = ['100M', '5G', '1G', '4G']
    max_size = ['2G', '16T', '32G', '16T']
    valid_size = r'^[1-9]{1}[0-9]{0,2}(,[0-9]{1,2}){0,1}(M|G|T){1}$'

    if (not re.match(valid_size, response)) \
            or ((size_counter(user) + parse_size(response
                                                 .replace(',', '.'))) >
                parse_size(drive.replace(',', '.'))) \
            or (parse_size(response.replace(',', '.')) <
                parse_size(min_size[index_counter(user)])) \
            or (parse_size(response.replace(',', '.')) >
                parse_size(max_size[index_counter(user)])):

        raise errors.ValidationError('', reason='Invalid size for {name}: \
{response} (e.q., {eq}) Minimum [{min}] Maximum [{max}] \
Remaining [{free}] test={t}'.format(
            name=name[index_counter(user)],
            response=response, eq=eq_size[index_counter(user)],
            min=min_size[index_counter(user)],
            max=max_size[index_counter(user)],
            free=format_size(parse_size(
                drive.replace(',', '.')) - size_counter(user))))

    return True


questions = [

    # Boot size
    inquirer.Text(
        'boot_size',
        message='Enter desired size for boot partition',
        validate=size_validation),

    # Root size
    inquirer.Text(
        'root_size',
        message='Enter desired size for root partition',
        default=None,
        validate=size_validation),

    # Swap size
    inquirer.Text(
        'swap_size',
        message='Enter desired size for swap partition',
        default=None,
        validate=size_validation),

    # Home size
    inquirer.Text(
        'home_size',
        message='Enter desired size for home partition',
        default=None,
        validate=size_validation)
]

user = inquirer.prompt(questions)
