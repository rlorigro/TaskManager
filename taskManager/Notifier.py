from email.message import EmailMessage
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

        # SMTP_SERVER = "smtp.gmail.com"
        # SMTP_PORT = 587
        if self.source_email is not None and self.source_password is not None:
            try:
                server = smtplib.SMTP('localhost')
            except ConnectionRefusedError:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(self.source_email, self.source_password)
        else:
            server = smtplib.SMTP('localhost')
        server.send_message(self.message)
        server.close()
