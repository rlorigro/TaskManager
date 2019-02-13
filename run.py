from modules.ProcessHandler import ProcessHandler
import argparse
import signal
import sys


def main(command, aws, sender, recipient, redirect_path):
    handler = ProcessHandler(aws=aws, email_sender=sender, email_recipient=recipient)

    signal.signal(signal.SIGTERM, handler.handle_exit)
    signal.signal(signal.SIGINT, handler.handle_exit)

    handler.launch_process(command, redirect_path=redirect_path)


def space_separated_arguments(string):
    arguments = string.strip().split(" ")
    return arguments


def string_as_bool(s):
    s = s.lower()
    boolean = None

    if s in {"t", "true", "1", "y", "yes"}:
        boolean = True
    elif s in {"f", "false", "0", "n", "no"}:
        boolean = False
    else:
        exit("Error: invalid argument specified for boolean flag: %s" % s)

    return boolean


def space_separated_list(s):
    tokens = s.strip().split(" ")
    return tokens


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.register("type", "bool", string_as_bool)
    parser.register("type", "space_separated_list", space_separated_list)

    parser.add_argument("--command", "-c",
                        dest="command",
                        required=True,
                        type=space_separated_list,
                        help="The command to be run inside a subprocess and monitored with email notification")

    parser.add_argument("--to",
                        dest="recipient",
                        required=True,
                        type=str,
                        help="A comma-separted list of email recipients (ie 'user1@domain.com,user2@domain.com'). For AWS, this must be validated within SES console")

    parser.add_argument("--from",
                        dest="sender",
                        required=True,
                        type=str,
                        help="The email sender. For AWS, this must be validated within SES console")

    parser.add_argument("--aws",
                        required=False,
                        default="True",
                        type=string_as_bool,
                        help="Whether to use AWS SES or simple local SMTP server")

    parser.add_argument("--redirect",
                        required=False,
                        type=str,
                        help="File name to redirect to")

    args = parser.parse_args()
    main(command=args.command, aws=args.aws, sender=args.sender, recipient=args.recipient, redirect_path=args.redirect)
