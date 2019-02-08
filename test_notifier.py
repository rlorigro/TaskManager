from modules.Notifier import Notifier


def main():
    recipient = "rlorigro@ucsc.edu"
    sender = "rlorigro@ucsc.edu"

    notifier = Notifier(email_recipient=recipient, email_sender=sender)

    subject = "Test"
    body = "sup"
    notifier.send_mail(subject, body)


if __name__ == "__main__":
    main()
