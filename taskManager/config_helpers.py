#!/usr/bin/env python
"""Helper tools for reading and writing a config file """
########################################################################
# File: config_helpers.py
#  executable: config_helpers.py
#
# Author: Andrew Bailey
# History: 04/01/19 Created
########################################################################

import os
import sys
from pathlib import Path
from py3helpers.utils import save_json, load_json, create_dot_dict


TM_HOME_DIR = os.path.join(str(Path.home()), ".taskmanager")
TM_CONFIG_PATH = os.path.join(TM_HOME_DIR, "config")


def write_task_manager_config(dict_args):
    """Write a config file
    :param dict_args: dictionary of arguments to write to config file
    """
    if not os.path.exists(TM_HOME_DIR):
        os.mkdir(TM_HOME_DIR)
    save_json(dict_args, TM_CONFIG_PATH)
    return TM_CONFIG_PATH


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via intput() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".

    https://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input
    """
    valid = {"yes": True, "y": True, "ye": True, "Y": True, "N": False,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def prompt_user_for_config_args():
    """Prompt user for arguments for config file"""
    config_args = {"sender": input("Sender Email: "), "recipient": None, "aws": False, "source_email": None,
                   "source_password": None}

    to_emails = []
    more_emals = True
    while more_emals:
        tmp_email = input("Recipient Email: ")
        to_emails.append(tmp_email)
        more_emals = bool(query_yes_no("Add more emails?"))
    config_args["recipient"] = to_emails
    config_args["aws"] = query_yes_no("Is this an aws server?")
    if not config_args["aws"]:
        config_args["source_email"] = input("Source email address: ")
        config_args["source_password"] = input("Source password: ")

    return config_args


def create_task_manager_config():
    """Prompt user for config file information and save it to predefined location"""
    args = prompt_user_for_config_args()
    write_task_manager_config(args)
    return True


def get_task_manager_config():
    """Read in taskManager config file"""
    assert os.path.exists(TM_CONFIG_PATH), "No config file: run 'taskManager configure' to setup config file"
    return create_dot_dict(load_json(TM_CONFIG_PATH))
