from taskManager.plotting import *
import argparse


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

    plot_resources_main(file_path=args.log_path, output_dir=args.output_dir)

