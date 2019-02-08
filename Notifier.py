import os


class Notifier:
    def __init__(self, email_sender, email_recipient, subject_prefix="<automated>"):
        self.email_sender = email_sender
        self.email_recipient = email_recipient
        self.subject_prefix = subject_prefix

    def send_mail(self, subject, body, subject_prefix=True):
        if subject_prefix:
            subject = self.subject_prefix + subject

        sendmail_location = "/usr/sbin/sendmail"
        p = os.popen("%s -t" % sendmail_location, "w")
        p.write("From: %s\n" % self.email_sender)
        p.write("To: %s\n" % self.email_recipient)
        p.write("Subject: %s\n\n" % subject)
        p.write(body)
        status = p.close()

        # if status != 0:
        #     print("Sendmail exit status", status)
