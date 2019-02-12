from modules.plotting import *
from datetime import datetime
import argparse
import errno
import os


def get_datetime_string():
    """
    Generate a datetime string. Useful for making output folders names that never conflict.
    """
    now = datetime.now()
    now = [now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond]
    datetime_string = "_".join(list(map(str, now)))

    return datetime_string


def ensure_directory_exists(directory_path):
    """
    Recursively test directories in a directory path and generate missing directories as needed
    :param directory_path:
    :return:
    """
    if not os.path.exists(directory_path):

        try:
            os.makedirs(directory_path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(directory_path):
                pass
            else:
                raise


def main(file_path, output_dir):
    headers, header_indexes, data = read_tsv(file_path)
    figure, axes = plot_resource_data(headers=headers, data=data, show=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--log_path",
        type=str,
        required=True,
        help="Input TSV file path containing the output of ResourceMonitor"
    )

    parser.add_argument(
        "--output_dir", "-o",
        type=str,
        default="./output/",
        required=False,
        help="Desired output directory path (will be created during run time if doesn't exist)"
    )

    args = parser.parse_args()

    main(file_path=args.log_path, output_dir=args.output_dir)

