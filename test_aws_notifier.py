from modules.AWSNotifier import Notifier


def main():
    recipient = "rlorigro@ucsc.edu"
    sender = "rlorigro@ucsc.edu"

    notifier = Notifier(email_recipient=recipient, email_sender=sender)

    subject = "Test"
    body = "success"
    notifier.send_message(subject, body)


if __name__ == "__main__":
    main()
