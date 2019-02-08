import smtplib
from email.message import EmailMessage


class Notifier:
    def __init__(self, email_sender, email_recipient, subject_prefix="<automated>"):
        self.email_sender = email_sender
        self.email_recipient = email_recipient
        self.subject_prefix = subject_prefix

    def send_mail(self, subject, body, subject_prefix=True):
        if subject_prefix:
            subject = self.subject_prefix + subject

        message = EmailMessage()

        message["Subject"] = subject
        message["From"] = self.email_sender
        message["To"] = self.email_recipient
        message.set_content(body)

        s = smtplib.SMTP('localhost')
        s.send_message(message)
        s.quit()

        # if status != 0:
        #     print("Sendmail exit status", status)
