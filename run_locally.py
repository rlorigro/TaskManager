from taskManager.ResourceMonitor import ResourceMonitor
from taskManager.ProcessHandler import ProcessHandler
import argparse
import os
import errno
import signal
import threading


def main(command, output_dir, interval, stderr, stdout):

    # create resource monitoring class
    monitor = ResourceMonitor(output_dir=output_dir,
                              interval=interval,
                              aws=False,
                              s3_upload_bucket=None,
                              s3_upload_path=None,
                              s3_upload_interval=None)

    # initialize process handler
    handler = ProcessHandler(aws=False,
                             email_sender=None,
                             email_recipients=None,
                             source_email=None,
                             source_password=None,
                             resource_monitor=monitor,
                             attach_full_log=False)

    # update signal handling rule with the process handler's member functions
    signal.signal(signal.SIGTERM, handler.handle_exit)
    signal.signal(signal.SIGINT, handler.handle_exit)

    # Launch process via the process handler
    handler.launch_process(command,
                           redirect_stdout=stdout,
                           redirect_stderr=stderr)


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
    parser.register("type", "string_as_bool", string_as_bool)


    parser.add_argument("--command", "-c",
                            dest="run_command",
                            required=True,
                            type=space_separated_list,
                            help="The command to be run inside a subprocess: eg. -c 'sleep 10' ")

    parser.add_argument("--redirect_stdout", "-r",
                            dest="redirect_stdout",
                            required=False,
                            default=None,
                            type=str,
                            help="Redirect stdout of command to a file")

    parser.add_argument('--redirect_stderr', '-e',
                            dest='redirect_stderr',
                            required=False,
                            default=None,
                            type=str,
                            help="Redirect stderr to a log file")

    parser.add_argument('--interval',
                            dest='interval',
                            required=False,
                            default=5,
                            type=int,
                            help="interval (in seconds) for sampling mem/cpu/IO usage")


    parser.add_argument('--output_dir',
                            dest='output_dir',
                            default="taskManager_output/",
                            type=str,
                            help="Output folder to place memory/cpu/IO usage log")


    args = parser.parse_args()

    main(command=args.run_command, output_dir=args.output_dir, interval=args.interval, stderr=args.redirect_stderr, stdout=args.redirect_stdout)