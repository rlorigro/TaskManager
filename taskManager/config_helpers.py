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


DefaultPaths = dict(home=os.path.join(str(Path.home()), ".taskmanager"),
                    output=os.path.join(os.path.join(str(Path.home()), ".taskmanager"),
                                               "resource_manager_output"),
                    config=os.path.join(os.path.join(str(Path.home()), ".taskmanager"), "config"))


def write_task_manager_config(dict_args):
    """Write a config file
    :param dict_args: dictionary of arguments to write to config file
    """
    # Make dirs
    if not os.path.exists(DefaultPaths["home"]):
        os.mkdir(DefaultPaths["home"])
    if not os.path.exists(DefaultPaths["output"]):
        os.mkdir(DefaultPaths["output"])
    save_json(dict_args, DefaultPaths["config"])
    return DefaultPaths["config"]


def query_yes_no(question, default=True):
    """Ask a yes/no question via intput() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the default return value True or False

    The "answer" return value is True for "yes" or False for "no".

    https://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input
    """
    valid = {"yes": True, "y": True, "ye": True, "Y": True, "N": False,
             "no": False, "n": False}
    prompt = " [y/n] "
    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def prompt_user_for_config_args():
    """Prompt user for arguments for config file"""
    config_args = {"sender": None, "recipient": None, "aws": False, "source_email": None,
                   "source_password": None, "resource_monitor": True,
                   "output_dir": DefaultPaths["output"], "s3_upload_bucket": None,
                   "s3_upload_path": "logs/resource_monitor/{date}_{instance_id}/",
                   "s3_upload_interval": 300, "interval": 5}

    if os.path.exists(DefaultPaths["config"]):
        config_args = create_dot_dict(load_json(DefaultPaths["config"]))

    config_args["sender"] = user_input_or_defualt("Sender Email", config_args["sender"], str)
    to_emails = []
    more_emails = True
    while more_emails:
        tmp_email = user_input_or_defualt("Recipient Email:", config_args["recipient"], str)
        if tmp_email is not None:
            to_emails.append(tmp_email)
            more_emails = query_yes_no("Add more emails?")
        else:
            more_emails = False
            to_emails = config_args["recipient"]

    config_args["recipient"] = to_emails

    config_args["aws"] = query_yes_no("Is this an aws server?", default=config_args["aws"])
    if not config_args["aws"]:
        config_args["source_email"] = user_input_or_defualt("Source email address", config_args["source_email"], str)
        config_args["source_password"] = user_input_or_defualt("Source password", config_args["source_password"], str)
    config_args["resource_monitor"] = query_yes_no("Monitor Compute Resources?",
                                                   default=config_args["resource_monitor"])
    if config_args["resource_monitor"]:
        config_args["output_dir"] = user_input_or_defualt("Output dir: ", config_args["output_dir"], str)
        config_args["interval"] = user_input_or_defualt("Access compute resources interval: ", config_args["interval"],
                                                        float)
        config_args["s3_upload_bucket"] = user_input_or_defualt("S3 Upload Bucket: ",
                                                                config_args["s3_upload_bucket"], str)
        config_args["s3_upload_path"] = user_input_or_defualt("S3 Upload Path: ",
                                                              config_args["s3_upload_path"], str)
        config_args["s3_upload_interval"] = user_input_or_defualt("S3 Upload Interval: ",
                                                                  config_args["s3_upload_interval"], int)

    return config_args


def user_input_or_defualt(message, default, type):
    """Get the user input from a message and revert to default value if user does not specify"""
    x = input(message + "[{}]:".format(default))
    if x is '':
        return default
    else:
        try:
            x = type(x)
        except Exception:
            raise TypeError("Wrong input type, must type in a {}".format(type))
        return type(x)


def create_task_manager_config():
    """Prompt user for config file information and save it to predefined location"""
    args = prompt_user_for_config_args()
    write_task_manager_config(args)
    return True


def get_task_manager_config():
    """Read in taskManager config file"""
    assert os.path.exists(DefaultPaths["config"]), "No config file: run 'taskManager configure' to setup config file"
    return create_dot_dict(load_json(DefaultPaths["config"]))

