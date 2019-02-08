from datetime import datetime
import psutil
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
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.log_filename = "log" + getDatetimeString() + ".txt"
        self.log_path = os.path.join(output_dir, self.log_filename)

    def launch(self):
        with open(self.log_path):
