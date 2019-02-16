from modules.ResourceMonitor import ResourceMonitor
from datetime import datetime
import argparse
import os
import errno
import boto3
import numpy as np
from collections import deque
from time import sleep


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


def handle_resource_monitor_log_file(log_file: ResourceMonitorLogFile, args):

    tmp_loc = os.path.join(args.tmp_dir, log_file.filename)
    if os.path.isfile(tmp_loc):
        print("Removing existing file: {}".format(tmp_loc))
        os.remove(tmp_loc)

    errors = list()

    try:
        s3 = boto3.resource('s3')
        s3.Bucket(log_file.bucket).download_file(log_file.path, tmp_loc)

        header = None
        last_lines = deque()
        line_count = 0
        with open(tmp_loc, 'r') as log_file_in:
            for line in log_file_in:
                if header is None:
                    header = {key:i for i, key in enumerate(line.strip().split("\t"))}
                    continue
                line_count += 1

                last_lines.append(line)
                if line_count > args.line_count:
                    last_lines.popleft()

        # count lines
        if log_file.total_lines is not None and line_count <= log_file.total_lines:
            errors.append("log file was not updated (curr: {}, prev: {})".format(line_count, log_file.total_lines))
        log_file.total_lines = line_count
        # empty file?
        if header is None:
            errors.append("file appears to be empty")
            return errors

        # make lines useful
        lines = list()
        for line in last_lines:
            line_parts = line.strip().split("\t")
            if len(line_parts) != len(header):
                errors.append("malformed file (header size: {}, line size: {}).  line: '{}'".format(
                    len(header), len(line_parts), "\\t".join(line_parts)))
                return errors
            lines.append({key:float(line_parts[header[key]]) for key in header.keys()})

        # analyze lines:
        averages = {key: np.mean(list(map(lambda line: line[key], lines))) for key in header.keys()}
        print(log_file.id)
        for key in header.keys():
            print("\t{}: {}".format(key, averages[key]))

        # find errors in lines
        CPU_PERCENT = "cpu_percent"
        DISK_USAGE_PERCENT = "disk_usage_percent"
        VIRTUAL_MEMORY_PERCENT = "virtual_memory_percent"

        if CPU_PERCENT not in header:
            errors.append("missing {} header".format(CPU_PERCENT))
        elif averages[CPU_PERCENT] < 50:
            errors.append("CPU usage below 50%: {}".format(averages[CPU_PERCENT]))

        if DISK_USAGE_PERCENT not in header:
            errors.append("missing {} header".format(DISK_USAGE_PERCENT))
        elif averages[DISK_USAGE_PERCENT] > 90:
            errors.append("Disk usage above 90%: {}".format(averages[DISK_USAGE_PERCENT]))

        if VIRTUAL_MEMORY_PERCENT not in header:
            errors.append("missing {} header".format(VIRTUAL_MEMORY_PERCENT))
        elif averages[VIRTUAL_MEMORY_PERCENT] > 90:
            errors.append("Memory usage above 90%: {}".format(averages[VIRTUAL_MEMORY_PERCENT]))


    except Exception as e:
        errors.append("Exception: {}".format(e))

    finally:
        # don't leave these around
        if os.path.isfile(tmp_loc): os.remove(tmp_loc)

    return errors


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

    # iterate over all files
    while (True):
        errors = dict()
        for file in files:
            file_errors = handle_resource_monitor_log_file(file, args)
            if len(file_errors) != 0:
                errors[file.id] = file_errors

        error_string = ''
        for file_id in errors.keys():
            error_string += "{}\n".format(file_id)
            for err in errors[file_id]:
                error_string += "\t{}\n".format(err)

        if len(error_string) != 0:
            print(("\n---------------------------------------------------\n"
                   "Errors at {}:\n\n{}"
                   "---------------------------------------------------")
                  .format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), error_string))

        sleep(args.interval)


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
                        default=660,
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


    args = parser.parse_args()
    if args.sources is None and args.source_file is None:
        raise Exception("One of --sources or --source_file parameter is required")

    main(args)
