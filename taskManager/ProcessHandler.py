from taskManager.Notifier import Notifier
from taskManager.AWSNotifier import Notifier as AWSNotifier
from taskManager.ResourceMonitor import get_instance_identification
from taskManager.plot_resource_usage import plot_resources_main
from time import time
import subprocess
import sys
import gc


class ProcessHandler:
    def __init__(self, aws=True, email_sender=None, email_recipients=None, source_email=None, source_password=None,
                 resource_monitor=None):
        self.email_sender = email_sender
        self.email_recipients = None
        if email_recipients is not None:
            self.email_recipients = email_recipients
        self.aws = aws

        self.process = None
        self.arguments = None
        self.start_time = None
        self.end_time = None
        self.attachment = None
        self.source_email = source_email
        self.source_password = source_password

        if aws:
            self.notifier = AWSNotifier(email_sender=email_sender, email_recipients=self.email_recipients)
        else:
            self.notifier = Notifier(email_sender=email_sender, email_recipients=self.email_recipients,
                                     source_password=self.source_password, source_email=self.source_email)

        self.resource_monitor = resource_monitor
        if self.resource_monitor is not None:
            self.resource_monitor.background_launch()

    def get_machine_name(self):
        if self.aws:
            prefix = "instance "
            suffix = get_instance_identification()
            name = prefix + suffix

        else:
            name = "local machine"

        return name

    def send_notification(self):
        argument_string = " ".join(self.arguments)
        machine_name = self.get_machine_name()
        time_elapsed = (self.end_time - self.start_time)/60

        subject = "Process concluded"
        body = "Process with the following arguments: \n\t%s \non %s has concluded after %.2f minutes." % \
               (argument_string, machine_name, time_elapsed)

        self.notifier.send_message(subject, body, attachment=self.attachment)

    def get_pid(self):
        if self.process is not None:
            return self.process.pid
        else:
            return None

    def launch_process(self, arguments, working_directory=".", redirect_path=None):
        self.arguments = arguments
        print("RUNNING: %s" % " ".join(arguments))

        if self.process is None:
            self.start_time = time()

            if redirect_path is None:
                self.process = subprocess.Popen(arguments, cwd=working_directory)
            else:
                with open(redirect_path, "w") as output_file:
                    print("REDIRECTING TO: ", redirect_path, "\n")
                    self.process = subprocess.Popen(arguments, cwd=working_directory, stdout=output_file)

            self.process.wait()
            self.end_time = time()
            if self.resource_monitor is not None:
                self.resource_monitor.kill()
                self.attachment = plot_resources_main(self.resource_monitor.log_path,
                                                      self.resource_monitor.output_dir,
                                                      show=False)
            self.send_notification()

        else:
            exit("ERROR: process already launched")
            self.resource_monitor.kill()

    def handle_exit(self, signum=None, frame=None):
        """
        Method to be called at (early) termination. By default, the native "signal" handler passes 2 arguments signum
        (signal number) and frame
        :param signum:
        :param frame:
        :return:
        """
        self.end_time = time()
        self.send_notification()

        sys.stderr.write("\nERROR: script terminated or interrupted killing subprocess: %d\n" % self.process.pid)

        self.kill()     # goodbye cruel world

        exit(1)

    def kill(self):
        if self.process is not None:
            self.process.kill()  # kill or terminate?
            self.process = None

            gc.collect()

        else:
            print("WARNING: no running process to be killed")
