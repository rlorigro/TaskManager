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
from taskManager.utils.config import load_json, save_json
import taskManager.utils.config as tm
from unittest.mock import patch
import tempfile


class TaskManagerTests(unittest.TestCase):
    """Test TaskManager"""

    @classmethod
    def setUpClass(cls):
        super(TaskManagerTests, cls).setUpClass()
        cls.HOME = '/'.join(os.path.abspath(__file__).split("/")[:-2])
        cls.test_image = os.path.join(cls.HOME, "output/log_20190401-134809-155319.png")

    def test_write_config(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tm.DefaultPaths = dict(home=os.path.join(tempdir, ".taskmanager"),
                                   output=os.path.join(os.path.join(tempdir, ".taskmanager"),
                                                       "resource_manager_output"),
                                   config=os.path.join(os.path.join(tempdir, ".taskmanager"), "config"))

            test = {"asdf": 1}
            path = tm.write_task_manager_config(test)
            data = load_json(path)
            self.assertDictEqual(test, data)

    def test_user_input_or_defualt(self):
        user_input = [5]
        with patch('builtins.input', side_effect=user_input):
            data = tm.user_input_or_default("test", 10, int)
            self.assertEqual(data, 5)
        user_input = ['']
        with patch('builtins.input', side_effect=user_input):
            data = tm.user_input_or_default("test", 10, int)
            self.assertEqual(data, 10)
        user_input = ['asdf']
        with patch('builtins.input', side_effect=user_input):
            self.assertRaises(TypeError, tm.user_input_or_default, "test", 10, int)
        user_input = ['asdf']
        with patch('builtins.input', side_effect=user_input):
            data = tm.user_input_or_default("test", 10, str)
            self.assertEqual(data, "asdf")
        user_input = ['']
        with patch('builtins.input', side_effect=user_input):
            data = tm.user_input_or_default("test", 10, str)
            self.assertEqual(data, 10)

    def test_prompt_user_for_config_args(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tm.DefaultPaths = dict(home=os.path.join(tempdir, ".taskmanager"),
                                   output=os.path.join(os.path.join(tempdir, ".taskmanager"),
                                                       "resource_manager_output"),
                                   config=os.path.join(os.path.join(tempdir, ".taskmanager"), "config"))

            user_input = [
                'some_email',
                'some_email2',
                'y',
                'some_email3',
                'n',
                'n',
                "some_email4",
                "some_password",
                'y',
                tm.DefaultPaths['output'],
                '',
                'n',
                'n'
            ]
            config_args = {"sender": "some_email",
                           "recipient": ["some_email2", "some_email3"],
                           "aws": False,
                           "source_email": "some_email4",
                           "source_password": "some_password",
                           "resource_monitor": True,
                           "output_dir": tm.DefaultPaths['output'],
                           "s3_upload_bucket": None,
                           "s3_upload_path": None,
                           "s3_upload_interval": None,
                           "interval": 5,
                           "attach_log": False}

            with patch('builtins.input', side_effect=user_input):
                stacks = tm.prompt_user_for_config_args()

            self.assertSequenceEqual(stacks, config_args)

    def test_create_task_manager_config(self):
        with tempfile.TemporaryDirectory() as tempdir:

            tm.DefaultPaths = dict(home=os.path.join(tempdir, ".taskmanager"),
                                   output=os.path.join(os.path.join(tempdir, ".taskmanager"),
                                                       "resource_manager_output"),
                                   config=os.path.join(os.path.join(tempdir, ".taskmanager"), "config"))
            user_input = [
                'some_email',
                'some_email2',
                'y',
                'some_email3',
                'n',
                'n',
                "some_email4",
                "some_password",
                "y",
                tm.DefaultPaths['output'],
                '',
                '',
                '',
                '',
                ''
            ]

            config_args = {"sender": "some_email",
                           "recipient": ["some_email2", "some_email3"],
                           "aws": False,
                           "source_email": "some_email4",
                           "source_password": "some_password",
                           "resource_monitor": True,
                           "output_dir": tm.DefaultPaths['output'],
                           "s3_upload_bucket": None,
                           "s3_upload_path": None,
                           "s3_upload_interval": None,
                           "interval": 5,
                           "attach_log": False}

            with patch('builtins.input', side_effect=user_input):
                stacks = tm.create_task_manager_config()
            self.assertTrue(stacks)
            self.assertDictEqual(config_args, load_json(tm.DefaultPaths["config"]))

    def test_get_task_manager_config(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tm.DefaultPaths = dict(home=os.path.join(tempdir, ".taskmanager"),
                                   output=os.path.join(os.path.join(tempdir, ".taskmanager"),
                                                       "resource_manager_output"),
                                   config=os.path.join(os.path.join(tempdir, ".taskmanager"), "config"))

            config_args = {"sender": "some_email",
                           "recipient": ["some_email2", "some_email3"],
                           "aws": False,
                           "source_email": "some_email4",
                           "source_password": "some_password",
                           "resource_monitor": True,
                           "output_dir": tm.DefaultPaths['output'],
                           "s3_upload_bucket": None,
                           "s3_upload_path": None,
                           "s3_upload_interval": None,
                           "interval": 5}

            os.mkdir(tm.DefaultPaths["home"])
            save_json(config_args, tm.DefaultPaths['config'])
            self.assertDictEqual(config_args,
                                 tm.get_task_manager_config())

    # def test_send_message_with_attachment(self):
    #     recipient = ["namefake148@gmail.com"]
    #     sender = "namefake148@gmail.com"
    #
    #     notifier = Notifier.Notifier(email_recipients=recipient, email_sender=sender,
    #                                  source_email="namefake148@gmail.com", source_password="password1234!")
    #
    #     subject = "Test"
    #     body = "success\n\tasdf\nasdf"
    #     notifier.send_message(subject, body, self.test_image)
    #     notifier.send_message(subject, body, attachment=None)

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
