from matplotlib import pyplot
from collections import defaultdict
from datetime import datetime
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


def read_tsv(file_path):
    """
    General method for converting a tsv into a dictionary of lists, assuming each key has an associated time series
    :param file_path:
    :return:
    """
    headers = None
    header_indexes = None

    # Each data type will have a list
    data = defaultdict(list)
    static_data = defaultdict(list)

    with open(file_path, "r") as file:
        for l, line in enumerate(file):
            line = line.strip().split("\t")
            if l == 0:
                static_headers = line
                static_header_indexes = {x: i for i, x in enumerate(line)}

            elif l == 1:
                for i, item in enumerate(line):
                    key = static_headers[i]
                    static_data[key].append(float(item))

            elif l == 2:
                headers = line
                header_indexes = {x: i for i, x in enumerate(line)}
            else:
                for i, item in enumerate(line):
                    key = headers[i]
                    data[key].append(float(item))

    return headers, header_indexes, data, static_headers, static_header_indexes, static_data


def get_color(key):
    if key.startswith("cpu"):
        color = (0.945, 0.267, 0.176)
    elif key.startswith("io") or key.startswith("disk"):
        color = (0.122, 0.498, 0.584)
    elif "memory" in key:
        color = (0.945, 0.71, 0.176)
    else:
        exit("ERROR: invalid element in data, no corresponding color: %s" % key)

    return color


def get_y_max(key, y):
    if key.endswith("percent"):
        y_max = 100
    else:
        y_max = max(10, max(y))

    return y_max


def get_y_label(key):
    labels = {"cpu_percent": "CPU (%)",
              "virtual_memory_percent": "Virtual Memory (%)",
              "disk_usage_percent": "Disk Usage (%)",
              "swap_memory_percent": "Swap Memory (%)",
              "io_activity_read_mb": "IO Read (MB)",
              "io_activity_write_mb": "IO Write (MB)",
              "io_activity_read_count": "IO Reads (#)",
              "io_activity_write_count": "IO Writes (#)"}

    label = labels[key]

    return label


def rescale_time(time):
    time = [x / 60 for x in time]

    return time


def get_absolute_y_labels(data, static_data, y_percent, key):
    totals_keys = {"cpu_percent":"cpu_total",
                   "virtual_memory_percent": "virtual_memory_total_gb",
                   "disk_usage_percent": "disk_usage_total_gb",
                   "swap_memory_percent": "swap_memory_total_gb"}

    total_key = totals_keys[key]
    total_available = static_data[total_key][0]

    max_used = max(y_percent) / 100 * total_available

    max_used = int(round(max_used))
    total_available = int(round(total_available))

    return max_used, total_available


def plot_resource_data(headers, data, static_data, show=False):
    time_series_axes = {"cpu_percent": (0, 0),
                        "virtual_memory_percent": (0, 1),
                        "disk_usage_percent": (1, 0),
                        "swap_memory_percent": (1, 1),
                        "io_activity_read_mb": (2, 0),
                        "io_activity_write_mb": (2, 1),
                        "io_activity_read_count": (3, 0),
                        "io_activity_write_count": (3, 1)}

    n_rows = 4
    n_cols = 2
    figure, axes = pyplot.subplots(nrows=n_rows, ncols=n_cols)

    x = data["time_elapsed_s"]
    x = rescale_time(x)
    zeros = [0 for i in range(len(x))]

    for key in time_series_axes:
        a, b = time_series_axes[key]
        y = data[key]

        color = get_color(key)
        line_width = 0.5

        y_max = get_y_max(y=y, key=key)

        if key.endswith("percent"):
            axes[a][b].plot([x[0], x[-1]], [y_max, y_max], linestyle="--", color=color, linewidth=line_width)

            max_used, total_available = get_absolute_y_labels(data=data,
                                                              static_data=static_data,
                                                              y_percent=y,
                                                              key=key)

            max_used = str(max_used)
            total_available = str(total_available)

            if not key.startswith("cpu"):
                max_used += " GB"
                total_available += " GB"

            twin_axes = axes[a][b].twinx()
            twin_axes.tick_params(axis='y', left=False, top=False, right=True, bottom=False,
                                  labelleft=False, labeltop=False, labelright=True, labelbottom=False)
            twin_axes.set_yticks([max(y), y_max])

            twin_axes.set_yticklabels([max_used, total_available])
            twin_axes.set_ylim(0, y_max * 1.1)

        axes[a][b].set_ylim(0, y_max * 1.1)
        axes[a][b].set_ylabel(get_y_label(key))
        axes[a][b].set_title(" ".join(key.split("_")[:-1]))
        axes[a][b].plot(x, data[key], color=color, linewidth=line_width)
        axes[a][b].fill_between(x, y1=zeros, y2=y, color=color, alpha=0.3)

        if a == n_rows - 1:
            axes[a][b].set_xlabel("Time (min)")

    figure.set_size_inches(8, 16)
    pyplot.subplots_adjust(hspace=0.5, wspace=0.7)

    if show:
        pyplot.show()
        pyplot.close()

    return figure, axes


def plot_resources_main(file_path, output_dir, show=False):
    headers, header_indexes, data, static_headers, static_header_indexes, static_data = read_tsv(file_path)
    output_path = None

    if len(data) == 0:
        print("No data recorded in {}".format(file_path))
    else:
        output_filename_prefix = os.path.basename(file_path).split(".")[0]
        output_filename = output_filename_prefix + ".png"
        output_path = os.path.join(output_dir, output_filename)

        figure, axes = plot_resource_data(headers=headers, data=data, static_data=static_data, show=show)
        print("Saving figure as: %s" % output_path)
        figure.savefig(output_path, dpi=300)

    return output_path


"""

#####  Color Palette by Paletton.com
#####  Palette URL: http://paletton.com/#uid=33n0u0kq2ugg9F-lgx5u2pIwokm


*** Primary color: BLUE

   shade 0 = #1F7F95 = rgb( 31,127,149) = rgba( 31,127,149,1) = rgb0(0.122,0.498,0.584)
   shade 1 = #61ACBE = rgb( 97,172,190) = rgba( 97,172,190,1) = rgb0(0.38,0.675,0.745)
   shade 2 = #398DA1 = rgb( 57,141,161) = rgba( 57,141,161,1) = rgb0(0.224,0.553,0.631)
   shade 3 = #0B697F = rgb( 11,105,127) = rgba( 11,105,127,1) = rgb0(0.043,0.412,0.498)
   shade 4 = #035264 = rgb(  3, 82,100) = rgba(  3, 82,100,1) = rgb0(0.012,0.322,0.392)

*** Secondary color (1): YELLOW/ORANGE

   shade 0 = #F1B52D = rgb(241,181, 45) = rgba(241,181, 45,1) = rgb0(0.945,0.71,0.176)
   shade 1 = #FFD87E = rgb(255,216,126) = rgba(255,216,126,1) = rgb0(1,0.847,0.494)
   shade 2 = #FFCB56 = rgb(255,203, 86) = rgba(255,203, 86,1) = rgb0(1,0.796,0.337)
   shade 3 = #CD920D = rgb(205,146, 13) = rgba(205,146, 13,1) = rgb0(0.804,0.573,0.051)
   shade 4 = #A27100 = rgb(162,113,  0) = rgba(162,113,  0,1) = rgb0(0.635,0.443,0)

*** Secondary color (2): RED

   shade 0 = #F1442D = rgb(241, 68, 45) = rgba(241, 68, 45,1) = rgb0(0.945,0.267,0.176)
   shade 1 = #FF8D7E = rgb(255,141,126) = rgba(255,141,126,1) = rgb0(1,0.553,0.494)
   shade 2 = #FF6956 = rgb(255,105, 86) = rgba(255,105, 86,1) = rgb0(1,0.412,0.337)
   shade 3 = #CD230D = rgb(205, 35, 13) = rgba(205, 35, 13,1) = rgb0(0.804,0.137,0.051)
   shade 4 = #A21300 = rgb(162, 19,  0) = rgba(162, 19,  0,1) = rgb0(0.635,0.075,0)


#####  Generated by Paletton.com (c) 2002-2014
"""
