import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os


class Notifier:
    def __init__(self, email_sender, email_recipients, subject_prefix="<automated> ", max_cumulative_attempts=10):
        # This address must be verified with Amazon SES.
        self.email_sender = email_sender

        # is still in the sandbox, this address must be verified.
        self.email_recipients = email_recipients

        self.subject_prefix = subject_prefix
        self.message = None

        # Have any emails been successfully sent?
        self.sent = False

        # Do not allow this Notifier to attempt to send more than this many emails
        self.max_cumulative_attempts = max_cumulative_attempts
        self.client = boto3.client('ses', region_name="us-west-2")

        # How many attempts have been made
        self.attempts = 0

    def send_message(self, subject, body, subject_prefix=True, attachment=None):
        """
        Send an email through AWS SES. Adapted from AWS' own docs on using boto3:
        https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-using-sdk-python.html
        :param subject:
        :param body:
        :param subject_prefix:
        :return:
        """
        # Check whether limit has been exceeded
        if self.attempts > self.max_cumulative_attempts:
            print("WARNING: max email attempts exceeded for this Notifier, max=%d, sent=%d" % \
                  (self.max_cumulative_attempts, self.attempts))
            return

        self.generate_message(subject=subject, body=body, subject_prefix=subject_prefix, attachment=attachment)

        # The character encoding for the email.
        charset = "UTF-8"

        # Create a new SES resource and specify a region.
        # Try to send the email.
        try:
            response = self.client.send_raw_email(
                Source=self.message['From'],
                Destinations=self.email_recipients,
                RawMessage={'Data': self.message.as_string()})

            # Display an error if something goes wrong.
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(response['MessageId'])
            self.sent = True

        self.attempts += 1

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
