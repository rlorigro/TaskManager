from email.message import EmailMessage
import smtplib
import os


class Notifier:
    def __init__(self, email_sender, email_recipient, subject_prefix="<automated>"):
        self.email_sender = email_sender
        self.email_recipient = email_recipient
        self.subject_prefix = subject_prefix

        self.message = None

    def generate_message(self, subject, body, subject_prefix=True):
        if subject_prefix:
            subject = self.subject_prefix + subject

        self.message = EmailMessage()

        self.message["Subject"] = subject
        self.message["From"] = self.email_sender
        self.message["To"] = self.email_recipient
        self.message.set_content(body)

    def send_message(self, aws=False):
        if not aws:
            server = smtplib.SMTP('localhost')
            server.send_message(self.message)
            server.close()

        else:
            username = os.environ['USERNAME']
            password = os.environ['PASSWORD']
            host = os.environ['SMTPHOST']
            port = os.environ['SMTPPORT']

            server = smtplib.SMTP(host, port)
            server.ehlo()
            server.starttls()
            server.login(username, password)
            server.send_message(self.message)
            server.close()
