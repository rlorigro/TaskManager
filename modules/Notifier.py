from email.message import EmailMessage
import smtplib
import os


class Notifier:
    def __init__(self, email_sender, email_recipients, max_cumulative_attempts=10, subject_prefix="<automated> "):
        self.email_sender = email_sender
        self.email_recipients = email_recipients
        self.subject_prefix = subject_prefix

        self.message = None
        self.sent = False

        # Do not allow this Notifier to attempt to send more than this many emails
        self.max_cumulative_attempts = max_cumulative_attempts

        # How many attempts have been made
        self.attempts = 0

    def generate_message(self, subject, body, subject_prefix=True):
        if subject_prefix:
            subject = self.subject_prefix + subject

        self.message = EmailMessage()

        self.message["Subject"] = subject
        self.message["From"] = self.email_sender
        self.message["To"] = self.email_recipients
        self.message.set_content(body)

    def send_message(self, subject, body):
        # Check whether limit has been exceeded
        if self.attempts > self.max_cumulative_attempts:
            print("WARNING: max email attempts exceeded for this Notifier, max=%d, sent=%d" % \
                  (self.max_cumulative_attempts, self.attempts))
            return

        self.generate_message(subject=subject, body=body)

        server = smtplib.SMTP('localhost')
        server.send_message(self.message)
        server.close()
