#!/usr/bin/env python
"""Testing TaskManager """
########################################################################
# File: test_taskmanager.py
#  executable: test_taskmanager.py
#
# Author: Andrew Bailey
# History: 03/30/19 Created
########################################################################

import unittest
import os
from taskManager import Notifier
from taskManager import AWSNotifier
import taskManager.config_helpers as tm
from py3helpers.utils import load_json, save_json
from unittest.mock import patch
import tempfile

class TaskManagerTests(unittest.TestCase):
    """Test TaskManager"""

    @classmethod
    def setUpClass(cls):
        super(TaskManagerTests, cls).setUpClass()
        cls.HOME = '/'.join(os.path.abspath(__file__).split("/")[:-1])

    def test_write_config(self):
        with tempfile.TemporaryDirectory() as tempdir:
            test = {"asdf": 1}
            tm.TM_HOME_DIR = os.path.join(tempdir, ".taskmanager")
            tm.TM_CONFIG_PATH = os.path.join(tempdir, "config")
            path = tm.write_task_manager_config(test)
            data = load_json(path)
            self.assertDictEqual(test, data)

    def test_prompt_user_for_config_args(self):
        user_input = [
            'some_email',
            'some_email2',
            'y',
            'some_email3',
            'n',
            'n',
            "some_email4",
            "some_password"
        ]
        config_args = {"from_email": "some_email", "to_emails": ["some_email2", "some_email3"], "aws": False,
                       "source_email": "some_email4",
                       "source_password": "some_password"}

        with patch('builtins.input', side_effect=user_input):
            stacks = tm.prompt_user_for_config_args()
        self.assertSequenceEqual(stacks, config_args)

    def test_create_task_manager_config(self):
        with tempfile.TemporaryDirectory() as tempdir:

            user_input = [
                'some_email',
                'some_email2',
                'y',
                'some_email3',
                'n',
                'n',
                "some_email4",
                "some_password"
            ]
            config_args = {"from_email": "some_email", "to_emails": ["some_email2", "some_email3"], "aws": False,
                       "source_email": "some_email4",
                       "source_password": "some_password"}
            tm.TM_HOME_DIR = os.path.join(tempdir, ".taskmanager")
            tm.TM_CONFIG_PATH = os.path.join(tempdir, "config")

            with patch('builtins.input', side_effect=user_input):
                stacks = tm.create_task_manager_config()
            self.assertTrue(stacks)
            self.assertDictEqual(config_args, load_json(tm.TM_CONFIG_PATH))

    def test_get_task_manager_config(self):
        self.assertRaises(AssertionError, tm.get_task_manager_config)
        with tempfile.TemporaryDirectory() as tempdir:

            config_args = {"from_email": "some_email", "to_emails": ["some_email2", "some_email3"], "aws": False,
                           "source_email": "some_email4",
                           "source_password": "some_password"}
            tm.TM_HOME_DIR = os.path.join(tempdir, ".taskmanager")
            tm.TM_CONFIG_PATH = os.path.join(tempdir, "config")
            save_json(config_args, tm.TM_CONFIG_PATH)
            self.assertDictEqual(config_args, 
                                 tm.get_task_manager_config())


    # def test_notifier(self):
    #     recipient = "namefake148@gmail.com"
    #     sender = "namefake148@gmail.com"
    #
    #     notifier = Notifier.Notifier(email_recipients=recipient, email_sender=sender)
    #
    #     subject = "Test"
    #     body = "success"
    #     notifier.send_message_via_gmail(subject, body)

    # def test_aws_notifier(self):
    #     recipient = "andbaile@ucsc.edu"
    #     sender = "andbaile@ucsc.edu"
    #
    #     notifier = AWSNotifier.Notifier(email_recipients=recipient, email_sender=sender)
    #
    #     subject = "Test"
    #     body = "success"
    #     notifier.send_message(subject, body)


if __name__ == '__main__':
    unittest.main()
