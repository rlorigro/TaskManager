import boto3
from botocore.exceptions import ClientError


class Notifier:
    def __init__(self, email_sender, email_recipient, subject_prefix="<automated>"):
        # This address must be verified with Amazon SES.
        self.email_sender = email_sender

        # is still in the sandbox, this address must be verified.
        self.email_recipient = email_recipient

        self.subject_prefix = subject_prefix
        self.message = None

    def send_message(self, subject, body, subject_prefix=True):
        if subject_prefix:
            subject = self.subject_prefix + subject

        # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
        aws_region = "us-west-2"

        # The HTML body of the email.
        body_html = """<html>
        <head></head>
        <body>
          <h1>Amazon SES Test (SDK for Python)</h1>
          <p>This email was sent with
            <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
            <a href='https://aws.amazon.com/sdk-for-python/'>
              AWS SDK for Python (Boto)</a>.</p>
        </body>
        </html>
                    """

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
                        'Html': {
                            'Charset': charset,
                            'Data': body_html,
                        },
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
