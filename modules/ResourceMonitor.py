from collections import deque
from datetime import datetime
from time import time, sleep
import psutil
import sys
import os
import errno
import subprocess
import json
import socket
import boto3


def getDatetimeString():
    """
    Generate a datetime string. Useful for making output folders names that never conflict.
    """
    return datetime.now().strftime("%Y%m%d-%H%M%S-%f")

def getDateString():
    """
    Generate a date string. Useful for identifying output folders.
    """
    return datetime.now().strftime("%Y%m%d")

def getInstanceIdentification():
    """
    Gets an identifier for an instance.  Gets EC2 instanceId if possible, else local hostname
    """
    instance_id = socket.gethostname()
    try:
        # "special tactics" for getting instance data inside EC2
        instance_data = subprocess.check_output(
            ["curl", "--silent", "http://169.254.169.254/latest/dynamic/instance-identity/document"])
        # convert from json to dict
        instance_data = json.loads(instance_data)
        # get the instanceId
        if 'instanceId' in instance_data:
            instance_id = instance_data['instanceId']
    except:
        pass

    return instance_id


def ensureDirectoryExists(directoryPath, i=0):
    """
    Recursively test directories in a directory path and generate missing directories as needed
    :param directoryPath:
    :return:
    """
    if i > 3:
        print("WARNING: generating subdirectories of depth %d, please verify path is correct: %s" % (i, directoryPath))

    if not os.path.exists(directoryPath):

        try:
            os.makedirs(directoryPath)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(directoryPath):
                pass
            else:
                raise


class ResourceMonitor:
    def __init__(self, output_dir, interval, alarm_interval=60, s3_upload_bucket=None, s3_upload_path=None,
                 s3_upload_interval=300):
        self.output_dir = output_dir
        datetime_string = getDatetimeString()
        date = getDateString()
        instance_identifier = getInstanceIdentification()
        self.log_filename = "log_{}_{}.txt".format(datetime_string, instance_identifier)
        self.log_path = os.path.join(output_dir, self.log_filename)

        self.primary_partition = None
        self.set_primary_partition(self.find_unix_primary_partition())

        self.history_size = max(1,int(round(alarm_interval/interval)))
        self.history = deque()
        self.update_history(self.get_resource_data())

        self.interval = interval

        self.headers = {"time_elapsed_s":0,
                        "cpu_percent":1,
                        "virtual_memory_total_gb":2,
                        "virtual_memory_percent":3,
                        "swap_memory_total_gb":4,
                        "swap_memory_percent":5,
                        "io_activity_read_mb":6,
                        "io_activity_write_mb":7,
                        "io_activity_read_count":8,
                        "io_activity_write_count":9,
                        "disk_usage_total_gb":10,
                        "disk_usage_percent":11}

        self.normalized_types = {"io_activity_read_mb",
                                 "io_activity_write_mb",
                                 "io_activity_read_count",
                                 "io_activity_write_count"}

        self.start_time = None
        self.counter = 0

        if s3_upload_bucket is not None:
            s3_upload_bucket = s3_upload_bucket.lstrip("s3://")
        self.s3_upload_bucket = s3_upload_bucket
        self.s3_upload_path = s3_upload_path.format(
            instance_id=instance_identifier, timestamp=datetime_string, date=date).lstrip("/")

        self.s3_upload_interval = s3_upload_interval
        self.upload_to_s3 = s3_upload_bucket is not None and s3_upload_path is not None



    def update_history(self, data):
        self.history.append(data)

        if len(self.history) > self.history_size:
            self.history.popleft()

    def launch(self):
        ensureDirectoryExists(self.output_dir)
        print("Writing to log file: %s" % os.path.abspath(self.log_path))

        checkpoint_time = time()
        upload_time = time()
        self.start_time = checkpoint_time

        self.write_header()

        while True:
            if time() - checkpoint_time > self.interval:

                # get data and write to file
                data = self.get_resource_data()
                self.update_history(data)
                line = self.format_data_as_line(data)
                with open(self.log_path, 'a') as file:
                    file.write(line)

                self.counter += 1
                checkpoint_time = time()

                # upload to s3 (if appropriate)
                if self.upload_to_s3 and time() - upload_time > self.s3_upload_interval:
                    try:
                        self.upload_data_to_s3()
                    except Exception as e:
                        # do not die
                        print("Error uploading to S3: {}".format(e))
                        self.s3_upload_interval = self.s3_upload_interval * 2
                        print("Changing upload interval to: {}s".format(self.s3_upload_interval))
                    upload_time = time()

                sleep(1)

    @staticmethod
    def list_primary_partitions():
        disk_partitions = psutil.disk_partitions()

        for partition in disk_partitions:
            print(partition.device)

    def set_primary_partition(self, partition_name):
        partition_name = os.path.basename(partition_name)
        self.primary_partition = partition_name

    @staticmethod
    def find_unix_primary_partition():
        primary_partition = None
        disk_partitions = psutil.disk_partitions()

        for partition in disk_partitions:
            if partition.mountpoint == "/":
                primary_partition = partition.device
                break

        return primary_partition

    def write_header(self):
        with open(self.log_path, "w") as file:
            header_line = [item[0] for item in sorted(self.headers.items(), key=lambda x: x[1])]
            header_line = "\t".join(header_line) + "\n"
            file.write(header_line)

    def get_resource_data(self):
        data = dict()

        data["time_elapsed_s"] = time()

        cpu_percent = psutil.cpu_percent()
        data["cpu_percent"] = cpu_percent

        virtual_memory = psutil.virtual_memory()
        data["virtual_memory_total_gb"] = virtual_memory.total/(1024**3)
        data["virtual_memory_percent"] = virtual_memory.percent

        swap_memory = psutil.swap_memory()
        data["swap_memory_total_gb"] = swap_memory.total/(1024**3)
        data["swap_memory_percent"] = swap_memory.percent

        io_activity = psutil.disk_io_counters(perdisk=True)
        data["io_activity_read_mb"] = io_activity[self.primary_partition].read_bytes/(1024**2)
        data["io_activity_write_mb"] = io_activity[self.primary_partition].write_bytes/(1024**2)
        data["io_activity_read_count"] = io_activity[self.primary_partition].read_count
        data["io_activity_write_count"] = io_activity[self.primary_partition].write_count

        disk_usage = psutil.disk_usage("/")
        data["disk_usage_total_gb"] = disk_usage.total/(1024**3)
        data["disk_usage_percent"] = disk_usage.percent

        return data

    def format_data_as_line(self, data):
        print("intervals elapsed: %d" % self.counter)

        line = list()
        for item in sorted(self.headers.items(), key=lambda x: x[1]):
            key = item[0]
            value = data[key]

            # If psutil gives absolute (cumulative) values, then subtract the baseline for each interval
            if key in self.normalized_types:
                value -= self.history[-2][key]

            if key == "time_elapsed_s":
                value -= self.start_time

            line.append("%.3f" % value)

        line = "\t".join(line) + "\n"

        return line

    def upload_data_to_s3(self):
        endpoint = os.path.join(self.s3_upload_path, self.log_filename)
        print("Uploading {} to s3://{}/{}".format(self.log_path, self.s3_upload_bucket, endpoint))
        s3 = boto3.resource('s3')
        s3.meta.client.upload_file(self.log_path, self.s3_upload_bucket, endpoint)
