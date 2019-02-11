from collections import deque
from datetime import datetime
from time import time
import psutil
import sys
import os


def getDatetimeString():
    """
    Generate a datetime string. Useful for making output folders names that never conflict.
    """
    now = datetime.now()
    now = [now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond]
    datetimeString = "_".join(list(map(str, now)))

    return datetimeString


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
            os.mkdir(directoryPath)

        except FileNotFoundError:
            ensureDirectoryExists(os.path.dirname(directoryPath), i=i + 1)

            if not os.path.exists(directoryPath):
                os.mkdir(directoryPath)


class ResourceMonitor:
    def __init__(self, output_dir, interval, alarm_interval=60):
        self.output_dir = output_dir
        self.log_filename = "log_" + getDatetimeString() + ".txt"
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

        self.normalized_types = {"time_elapsed_s",
                                 "io_activity_read_mb",
                                 "io_activity_write_mb",
                                 "io_activity_read_count",
                                 "io_activity_write_count"}

        self.counter = 0

    def update_history(self, data):
        self.history.append(data)

        if len(self.history) > self.history_size:
            self.history.popleft()

    def launch(self):
        ensureDirectoryExists(self.output_dir)

        checkpoint_time = time()

        with open(self.log_path, "w") as file:
            header_line = [item[0] for item in sorted(self.headers.items(), key=lambda x: x[1])]
            header_line = "\t".join(header_line) + "\n"
            file.write(header_line)

            while True:
                if time() - checkpoint_time > self.interval:
                    checkpoint_time = time()

                    data = self.get_resource_data()
                    self.update_history(data)
                    line = self.format_data_as_line(data)
                    file.write(line)
                    file.flush()

                    self.counter += 1

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
        sys.stdout.write("\rintervals elapsed: %d" % self.counter)

        line = list()
        for item in sorted(self.headers.items(), key=lambda x: x[1]):
            key = item[0]
            value = data[key]

            # If psutil gives absolute (cumulative) values, then subtract the baseline for each interval
            if key in self.normalized_types:
                value -= self.history[-2][key]

            line.append("%.3f" % value)

        line = "\t".join(line) + "\n"

        return line
