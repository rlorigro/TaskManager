from taskManager.AWSNotifier import Notifier
from collections import defaultdict
from datetime import datetime
import argparse
import os
import errno
import boto3
import numpy as np
from collections import deque
from time import sleep, time
import sys


class ErrorTracker:
    def __init__(self, notifier, resource_logs, tmp_dir, interval, n_lines):
        """
        Periodically print summaries of log files, and send email warnings if logs show that resource usage has
        exceeded some min/max threshold
        :param notifier:
        :param resource_logs:
        :param tmp_dir:
        :param interval:
        :param alarm_interval:
        :param n_lines:
        """
        self.notifier = notifier
        self.last_notification = -sys.maxsize
        self.resource_logs = resource_logs
        self.tmp_dir = tmp_dir
        self.n_lines = n_lines
        self.interval = interval

        # self.averages_per_log = None
        self.errors_per_log = None                  # keep track of these to send one email at end of update

    def start(self):
        # iterate over all files
        while (True):
            # reset periodic values
            self.errors_per_log = defaultdict(list)

            for file in self.resource_logs:
                tmp_file_path = os.path.join(args.tmp_dir, file.filename)

                # Re-download files
                self.update_log(log_file=file, tmp_file_path=tmp_file_path)

                # Get relevant data
                if os.path.exists(tmp_file_path):
                    averages = self.read_log(file, tmp_file_path)

                    # Check resource usage
                    self.check_resource_usage_thresholds(averages=averages, log_id=file.id)

                    # remove when done
                    print("Removing existing file: {}".format(tmp_file_path))
                    os.remove(tmp_file_path)
    
            # Send notification if necessary
            errors_exist = sum(map(len, self.errors_per_log.values())) > 0
            if errors_exist:
                self.send_notification()

            # iterate
            sleep(self.interval)

    def generate_error_message(self):
        """
        Parse errors from last update and generate readable string from them
        :return:
        """
        error_string = ''
        for file_id in self.errors_per_log.keys():
            if len(self.errors_per_log[file_id]) == 0: continue
            error_string += "{}\n".format(file_id)
            for err in self.errors_per_log[file_id]:
                error_string += "\t{}\n".format(err)

        if len(error_string) != 0:
            error_message = ("\n---------------------------------------------------\n"
                             "Errors at {}:\n\n{}"
                             "---------------------------------------------------")\
                             .format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), error_string)
        else:
            error_message = ""

        return error_message


    def read_log(self, log_file, tmp_file_path):
        """
        Get relevant data from the resource log to print summaries and to decide whether to send a notification
        :param log_file:
        :return:
        """
        header = None
        last_lines = deque()
        line_count = 0

        with open(tmp_file_path, 'r') as log_file_in:
            for line in log_file_in:
                if header is None:
                    header = {key: i for i, key in enumerate(line.strip().split("\t"))}
                    continue
                line_count += 1

                last_lines.append(line)
                if line_count > line_count:
                    last_lines.popleft()

        # find dead logs (via line counts)
        if log_file.total_lines is not None and line_count <= log_file.total_lines:
            self.errors_per_log[log_file.id].append("log file was not updated (curr: {}, prev: {})".format(line_count, log_file.total_lines))

        log_file.total_lines = line_count

        # empty file?
        if header is None:
            self.errors_per_log[log_file.id].append("file appears to be empty")
            return

        # make lines useful
        lines = list()
        for line in last_lines:
            line_parts = line.strip().split("\t")
            if len(line_parts) != len(header):
                self.errors_per_log[log_file.id].append("malformed file (header size: {}, line size: {}).  line: '{}'".format(
                    len(header), len(line_parts), "\\t".join(line_parts)))
                return

            lines.append({key:float(line_parts[header[key]]) for key in header.keys()})

        # analyze lines:
        averages = {key: np.mean(list(map(lambda line: line[key], lines))) for key in header.keys()}
        print(log_file.id)
        for key in header.keys():
            print("\t{}: {}".format(key, averages[key]))

        return averages

    def check_resource_usage_thresholds(self, averages, log_id):
        """
        Test for an alarming usage of resources!
        :param averages:
        :param log_id:
        :return:
        """
        CPU_PERCENT = "cpu_percent"
        DISK_USAGE_PERCENT = "disk_usage_percent"
        VIRTUAL_MEMORY_PERCENT = "virtual_memory_percent"

        if CPU_PERCENT not in averages:
            self.errors_per_log[log_id].append("missing {} header".format(CPU_PERCENT))
        elif averages[CPU_PERCENT] < 20:
            self.errors_per_log[log_id].append("CPU usage below 20%: {}".format(averages[CPU_PERCENT]))

        if DISK_USAGE_PERCENT not in averages:
            self.errors_per_log[log_id].append("missing {} header".format(DISK_USAGE_PERCENT))
        elif averages[DISK_USAGE_PERCENT] > 90:
            self.errors_per_log[log_id].append("Disk usage above 90%: {}".format(averages[DISK_USAGE_PERCENT]))

        if VIRTUAL_MEMORY_PERCENT not in averages:
            self.errors_per_log[log_id].append("missing {} header".format(VIRTUAL_MEMORY_PERCENT))
        elif averages[VIRTUAL_MEMORY_PERCENT] > 90:
            self.errors_per_log[log_id].append("Memory usage above 90%: {}".format(averages[VIRTUAL_MEMORY_PERCENT]))

    def update_log(self, tmp_file_path, log_file):
        """
        Query s3 to get latest log files
        :param log_file:
        :return:
        """
        if os.path.isfile(tmp_file_path):
            print("Removing existing file: {}".format(tmp_file_path))

            os.remove(tmp_file_path)

        try:
            s3 = boto3.resource('s3')
            s3.Bucket(log_file.bucket).download_file(log_file.path, tmp_file_path)

        except Exception as e:
            self.errors_per_log[log_file.id].append("Exception: {}".format(e))

    def send_notification(self):
        """
        Like the name says... Email all of the recipients declared within the notifier object about whatever was found
        this term
        :return:
        """
        subject = "Periodic update"
        body = self.generate_error_message()
        print(body)

        if self.notifier is not None:
            print("Sending notification email.")
            self.notifier.send_message(subject=subject, body=body)
        else:
            print("WARNING: Not sending notification email.")

        self.last_notification = time()


class ResourceMonitorLogFile:
    def __init__(self, log_file_location, id=None):
        if log_file_location.startswith("s3://"):
            log_file_location = log_file_location.replace("s3://", "")

        # file location data
        lfl_parts = log_file_location.split("/")
        self.bucket = lfl_parts[0]
        self.path = "/".join(lfl_parts[1:])
        self.filename = lfl_parts[-1]
        self.id = self.filename if id is None else id

        # file contents
        self.total_lines = None


def main(args):
    # ensure temp directory
    if not os.path.isdir(args.tmp_dir):
        try:
            os.makedirs(args.tmp_dir)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(args.output_dir):
                pass
            else:
                raise

    # get all files
    files = list()
    if args.sources is not None:
        sources = args.sources.split(",")
        for source in sources:
            files.append(ResourceMonitorLogFile(source.strip()))
    else:
        with open(args.source_file, 'r') as source_file:
            for line in source_file:
                if len(line.strip()) == 0 or line.startswith("#"): continue
                line_parts = line.split()
                files.append(ResourceMonitorLogFile(line_parts[0], id=None if len(line_parts) == 1 else ".".join(line_parts[1:])))

    if len(files) == 0:
        raise Exception("No source files found!")

    if args.recipients is not None and args.sender is not None:
        recipients = args.recipients.split(",")
        notifier = Notifier(email_recipients=recipients, email_sender=args.sender, max_cumulative_attempts=1000)
    else:
        print("\n\nWARNING:\nNo notifications will be sent!\n")
        notifier = None

    tracker = ErrorTracker(resource_logs=files,
                           interval=args.interval,
                           notifier=notifier,
                           tmp_dir=args.tmp_dir,
                           n_lines=args.line_count)

    tracker.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--sources', '-i',
                        dest='sources',
                        required=False,
                        default=None,
                        type=str,
                        help="Comma-separated list of resource usage locations (in s3).  "
                             "One of this param or --source_file is required.")
    parser.add_argument('--source_file', '-I',
                        dest='source_file',
                        required=False,
                        default=None,
                        type=str,
                        help="File listing the resource usage locations (in s3).  "
                             "One of this param or --sources is required.")
    parser.add_argument('--interval', '-t',
                        dest='interval',
                        required=False,
                        default=900,
                        type=int,
                        help="interval (in seconds) for downloading and verifying")
    parser.add_argument('--tmp_dir', '-d',
                        dest='tmp_dir',
                        required=False,
                        default="/tmp",
                        type=str,
                        help="tmp directory for downloading")
    parser.add_argument('--recent_history_line_count', '-l',
                        dest='line_count',
                        required=False,
                        default=30,
                        type=int,
                        help="how many lines (at the end of the file) to analyze")
    parser.add_argument("--to",
                        dest="recipients",
                        required=False,
                        default=None,
                        type=str,
                        help="A comma-separted list of email recipients (ie 'user1@domain.com,user2@domain.com'). For AWS, this must be validated within SES console")

    parser.add_argument("--from",
                        dest="sender",
                        required=False,
                        default=None,
                        type=str,
                        help="The email sender. For AWS, this must be validated within SES console")

    args = parser.parse_args()
    if args.sources is None and args.source_file is None:
        raise Exception("One of --sources or --source_file parameter is required")

    main(args)

