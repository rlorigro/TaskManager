from modules.ResourceMonitor import ResourceMonitor
import argparse
import os
import errno


def main(args):
    if not os.path.isdir(args.output_dir):
        try:
            os.makedirs(args.output_dir)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(args.output_dir):
                pass
            else:
                raise

    monitor = ResourceMonitor(output_dir=args.output_dir, interval=args.interval,
                              s3_upload_bucket=args.s3_upload_bucket, s3_upload_path=args.s3_upload_path,
                              s3_upload_interval=args.s3_upload_interval)

    monitor.launch()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--output_dir', '-o',
                        dest='output_dir',
                        required=False,
                        default="output",
                        type=str,
                        help="output folder")
    parser.add_argument('--interval', '-i',
                        dest='interval',
                        required=False,
                        default=15,
                        type=int,
                        help="interval (in seconds) for sampling")
    parser.add_argument('--s3_upload_interval', '-I',
                        dest='s3_upload_interval',
                        required=False,
                        default=300,
                        type=int,
                        help="interval (in seconds) for sampling")
    parser.add_argument('--s3_upload_bucket', '-b',
                        dest='s3_upload_bucket',
                        required=False,
                        default=None,
                        type=str,
                        help="bucket (s3:// is not required) for file uploading.  Setting this triggers upload.")
    parser.add_argument('--s3_upload_path', '-p',
                        dest='s3_upload_path',
                        required=False,
                        default="logs/resource_monitor/{date}_{instance_id}/",
                        type=str,
                        help="s3 location (no bucket) where logs should be uploaded.  "
                             "Can use custom python formatting parameters (need ':' prepended) including: "
                             "'instance_id', 'timestamp', 'date'.  "
                             "Default: 'logs/resource_monitor/{date}_{instance_id}/' ")

    args = parser.parse_args()
    main(args)
