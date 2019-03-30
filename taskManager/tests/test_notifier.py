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


class TaskManagerTests(unittest.TestCase):
    """Test TaskManager"""

    @classmethod
    def setUpClass(cls):
        super(TaskManagerTests, cls).setUpClass()
        cls.HOME = '/'.join(os.path.abspath(__file__).split("/")[:-1])

    def test_notifier(self):
        recipient = "andbaile@ucsc.edu"
        sender = "andbaile@ucsc.edu"

        notifier = Notifier.Notifier(email_recipients=recipient, email_sender=sender)

        subject = "Test"
        body = "success"
        notifier.send_message(subject, body)

    def test_aws_notifier(self):
        recipient = "andbaile@ucsc.edu"
        sender = "andbaile@ucsc.edu"

        notifier = AWSNotifier.Notifier(email_recipients=recipient, email_sender=sender)

        subject = "Test"
        body = "success"
        notifier.send_message(subject, body)


if __name__ == '__main__':
    unittest.main()
