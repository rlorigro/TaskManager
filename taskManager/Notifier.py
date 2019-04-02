#!/usr/bin/env python

from email.message import EmailMessage
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
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

    def generate_message(self, subject, body, subject_prefix=True, attachment=None):
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
        if attachment is not None:
            # open the file to be sent
            filename = os.path.basename(attachment)
            attachment = open(attachment, "rb")
            p = MIMEBase('application', 'octet-stream')
            # To change the payload into encoded form
            p.set_payload(attachment.read())
            # encode into base64
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
            # attach the instance 'p' to instance 'msg'
            self.message.attach(p)

    def send_message(self, subject, body, attachment=None):
        # Check whether limit has been exceeded
        if self.attempts > self.max_cumulative_attempts:
            print("WARNING: max email attempts exceeded for this Notifier, max=%d, sent=%d" % \
                  (self.max_cumulative_attempts, self.attempts))
            return

        self.generate_message(subject=subject, body=body, attachment=attachment)

        if self.source_email is not None and self.source_password is not None:
            try:
                server = smtplib.SMTP('localhost')
            except ConnectionRefusedError:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(self.source_email, self.source_password)
        else:
            server = smtplib.SMTP('localhost')
        # sending the mail
        server.sendmail(self.email_sender, self.email_recipients, self.message.as_string())
        server.close()
