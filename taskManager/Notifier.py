#!/usr/bin/env python

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from taskManager.utils.mail import *
import smtplib
import os


class Notifier:
    def __init__(self, email_sender, email_recipients, max_cumulative_attempts=10, subject_prefix="<automated> ",
                 source_email=None, source_password=None):
        self.email_sender = email_sender
        self.email_recipients = email_recipients
        self.subject_prefix = subject_prefix

        self.message = None
        self.sent = False
        self.source_email = source_email
        self.source_password = source_password
        # Do not allow this Notifier to attempt to send more than this many emails
        self.max_cumulative_attempts = max_cumulative_attempts

        # How many attempts have been made
        self.attempts = 0
        self.server = self.connect_to_server()
        self.server.close()

    def connect_to_server(self):
        """Check to see if we can connect to a server"""
        try:
            server = smtplib.SMTP('localhost')
        except ConnectionRefusedError:
            if self.source_email is not None and self.source_password is not None:
                try:
                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    server.login(self.source_email, self.source_password)
                except ConnectionRefusedError:
                    raise ConnectionRefusedError("Failed to connect to SMTP localhost and smtp.gmail.com. Double check "
                                                 "gmail credentials with --source_email and --source_password.")

            else:
                raise ConnectionRefusedError("Failed to connect to SMTP localhost. If on aws set --aws or use "
                                             "gmail with --source_email and --source_password.")
        return server

    def generate_message(self, subject, body, subject_prefix=True, attachments_paths=None):
        """Generate a message to send via the sendmail module of SMTP
        """
        if subject_prefix:
            subject = self.subject_prefix + subject

        # instance of MIMEMultipart
        self.message = MIMEMultipart()
        self.message['From'] = self.email_sender
        self.message['To'] = ", ".join(self.email_recipients)
        self.message['Subject'] = subject
        self.message.attach(MIMEText(body, 'plain'))

        if attachments_paths is not None:
            args = parse_paths_as_list(attachments_paths)

            for path in args:
                print("Attaching file to email: %s" % path)
                attachment = encode_attachment(path)

                if os.stat(path).st_size > 20*1000*1000:
                    print("File larger than 20MB not attached to email: %s")
                    continue

                # attach the instance 'attachment' to instance 'msg'
                self.message.attach(attachment)

    def send_message(self, subject, body, subject_prefix=True, attachment=None):
        # Check whether limit has been exceeded
        if self.attempts > self.max_cumulative_attempts:
            print("WARNING: max email attempts exceeded for this Notifier, max=%d, sent=%d" % \
                  (self.max_cumulative_attempts, self.attempts))
            return
        self.server = self.connect_to_server()

        self.generate_message(subject=subject, body=body, subject_prefix=subject_prefix, attachments_paths=attachment)
        # sending the mail
        self.server.sendmail(self.email_sender, self.email_recipients, self.message.as_string())
        self.server.close()
