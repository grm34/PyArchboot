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
import json
import logging
import os
import shlex
import sys
from subprocess import (PIPE, CalledProcessError, Popen, SubprocessError,
                        TimeoutExpired, check_output)

from requests import ReadTimeout, get


def run_command(cmd, args=None, error=None, exit_on_error=False):
    """Subprocess Popen with console output.

    Arguments:
        cmd -- String containing the shell command to run

    Keyword Arguments:
        args -- Array of the arguments to pipe (default: {None}),
        exit_on_error {boolean} -- Exit on exception (default: {False})

    Modules:
        subprocess -- Connect to input/output/error pipes and obtain return,
        shlex -- Analyzer class for simple shell-like syntaxes,
        logging -- Event logging system for applications and libraries,
        sys -- Access to some objects used or maintained by the interpreter

    Returns:
        output -- Run command and print the output to console
    """
    try:
        if args is not None:
            pipe = Popen(args, stdout=PIPE)
            command = Popen(shlex.split(cmd), stdin=pipe.stdout, stdout=PIPE,
                            encoding='utf-8')
            command = command.communicate()[0]
        else:
            command = Popen(shlex.split(cmd), stdin=PIPE, stdout=PIPE,
                            encoding='utf-8')

    except (SubprocessError, OSError, ValueError) as cmd_error:
        if error is not None:
            cmd_error = error

        if exit_on_error is True:
            logging.error(cmd_error)
            sys.exit(1)
        else:
            logging.debug(cmd_error)

    while True:
        output = command.stdout.readline()
        if output:
            logging.debug(output.strip())
            print(output.strip())
        else:
            break

    output = command.poll()
    return output


def command_output(cmd, exit_on_error=False, error=None, timeout=None):
    """Subprocess check_output with return codes.

    Arguments:
        cmd -- String containing the shell command to run

    Keyword Arguments:
        exit_on_error {boolean} -- Exit on exception (default: {False}),
        error -- String to set custom error message (default: {None}),
        timeout -- Integer to set timeout expired exception (default: {None})

    Modules:
        subprocess -- Connect to input/output/error pipes and obtain return,
        logging -- Event logging system for applications and libraries,
        sys -- Access to some objects used or maintained by the interpreter

    Returns:
        output -- Run command and return its output
    """
    try:
        output = check_output(cmd, shell=True, encoding='utf-8',
                              timeout=timeout)

    except (TimeoutExpired, CalledProcessError) as cmd_error:
        output = False

        if error is not None:
            cmd_error = error

        if exit_on_error is True:
            logging.error(cmd_error)
            sys.exit(1)
        else:
            logging.debug(cmd_error)

    return output


def api_json_ouput(url, exit_on_error=False, error=None, timeout=None):
    """JSON API url parser.

    Arguments:
        url -- String containing the url to parse

    Keyword Arguments:
        exit_on_error {boolean} -- Exit on exception (default: {False}),
        error -- String to set custom error message (default: {None}),
        timeout -- Integer to set timeout expired exception (default: {None})

    Returns:
        output -- Dictionary containing the json output
    """
    try:
        output = get(url, timeout=timeout).json()

    except (ConnectionError, ReadTimeout) as url_error:
        if error is not None:
            url_error = error
        logging.error(url_error)

        if exit_on_error is True:
            sys.exit(1)

    return output


def load_json_file(file):
    """JSON file parser.

    Arguments:
        file -- String containing the desired file to parse
                (should be in json folder)

    Modules:
        json -- JavaScript syntax data interchange format,
        os -- Export all functions from posix

    Returns:
        output -- Dictionary containing the json file
    """
    with open('{path}/json/{file}'.format(
            path=os.getcwd(), file=file), 'r', encoding='utf-8') as output:
        output = json.load(output)

    return output


# PyArchboot - Python Arch Linux Installer by grm34 under Apache License 2.0
##############################################################################
