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

        self.generate_message(subject=subject, body=body, subject_prefix=subject_prefix, attachments_paths=attachment)

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

    def parse_attachment_argument(self, arg):
        """
        Allow singular string path or list
        :param arg:
        :return:
        """
        invalid_argument = False

        if type(arg) is str:
            arg = [arg]

        elif type(arg) is list:
            for item in arg:
                if type(item) is not str:
                    invalid_argument = True

        else:
            invalid_argument = True

        if invalid_argument:
            exit("ERROR: invalid attachment argument. Must be string or list of strings, but found: %s" % str(arg))

        return arg

    def encode_attachment(self, attachment_path):
        # open the file to be sent
        filename = os.path.basename(attachment_path)
        attachments_paths = open(attachment_path, "rb")

        attachment = MIMEBase('application', 'octet-stream')

        # To change the payload into encoded form
        attachment.set_payload(attachments_paths.read())

        # encode into base64
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', "attachment; filename= %s" % filename)

        return attachment

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
            args = self.parse_attachment_argument(attachments_paths)

            for path in args:
                print("Attaching file to email: %s" % path)
                attachment = self.encode_attachment(path)

                if os.stat(path).st_size > 20*1000*1000:
                    print("File larger than 20MB not attached to email: %s")
                    continue

                # attach the instance 'attachment' to instance 'msg'
                self.message.attach(attachment)
