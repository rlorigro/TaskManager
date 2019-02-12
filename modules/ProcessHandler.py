import subprocess
import sys
import gc


class ProcessHandler:
    def __init__(self,  process=None):
        self.process = process

    def get_pid(self):
        if self.process is not None:
            return self.process.pid
        else:
            return None

    def launch_process(self, arguments, working_directory, wait):
        if self.process is None:

            self.process = subprocess.Popen(arguments, cwd=working_directory)
            if wait:
                self.process.wait()

        else:
            exit("ERROR: process already launched")

    def handle_exit(self, signum=None, frame=None):
        """
        Method to be called at (early) termination. By default, the native "signal" handler passes 2 arguments signum
        (signal number) and frame
        :param signum:
        :param frame:
        :return:
        """
        self.kill()     # goodbye cruel world

        sys.stderr.write("\nERROR: script terminated or interrupted killing subprocess: %d\n" % self.process.pid)

        exit(1)

    def kill(self):
        if self.process is not None:
            self.process.kill()  # kill or terminate?
            self.process = None

            gc.collect()

        else:
            print("WARNING: no running process to be killed")
