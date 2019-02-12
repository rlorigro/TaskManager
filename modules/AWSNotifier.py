import boto3
from botocore.exceptions import ClientError


class Notifier:
    def __init__(self, email_sender, email_recipient, subject_prefix="<automated> ", max_cumulative_attempts=10):
        # This address must be verified with Amazon SES.
        self.email_sender = email_sender

        # is still in the sandbox, this address must be verified.
        self.email_recipient = email_recipient

        self.subject_prefix = subject_prefix
        self.message = None

        # Have any emails been successfully sent?
        self.sent = False

        # Do not allow this Notifier to attempt to send more than this many emails
        self.max_cumulative_attempts = max_cumulative_attempts

        # How many attempts have been made
        self.attempts = 0

    def send_message(self, subject, body, subject_prefix=True):
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

        if subject_prefix:
            subject = self.subject_prefix + subject

        # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
        aws_region = "us-west-2"

        # The character encoding for the email.
        charset = "UTF-8"

        # Create a new SES resource and specify a region.
        client = boto3.client('ses', region_name=aws_region)

        # Try to send the email.
        try:
            # Provide the contents of the email.
            response = client.send_email(
                Destination={
                    'ToAddresses': [
                        self.email_recipient,
                    ],
                },
                Message={
                    'Body': {
                        'Text': {
                            'Charset': charset,
                            'Data': body,
                        },
                    },
                    'Subject': {
                        'Charset': charset,
                        'Data': subject,
                    },
                },
                Source=self.email_sender,
            )
        # Display an error if something goes wrong.
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(response['MessageId'])
            self.sent = True

        self.attempts += 1
