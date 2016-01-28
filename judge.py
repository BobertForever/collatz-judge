import tempfile
import os
import queue
import threading
import subprocess
from submission import Submission

class Judge:

    docker_name = 'sandbox'
    runtime = 'python3'
    timeout = 15

    def __init__(self):
        self.queue = queue.Queue()
        threading.Thread(target=self.await_submission).start()

    """
    Busy wait until we get a submission. Once we get a submission, run the
    judge
    """
    def await_submission(self):
        while True:
            try:
                submission = self.queue.get(timeout=1)
                self.run_judge(submission)
            except queue.Empty:
                continue

    """
    Submit a submission to the judge for grading
    """
    def submit(self, submission):
        self.queue.put(submission)

    """
    Run a given submission on docker
    """
    def run_judge(self, submission):
        f = prepare_submission(submission)
        file_path = os.path.dirname(f.name)
        file_name = os.path.basename(f.name)

        # The judge now has the submission
        submission.state = Submission.RUNNING
        submission.save()

        # Setup the docker command we're going to run to test the submission
        docker_name = str(uuid.uuid4())
        docker_cmd = [
            'docker',
            'run',
            '--name="%s"' % docker_name,
            '-v',
            '"%s":/judging_dir:ro' % file_path,
            '-w',
            '/judging_dir',
            self.docker_name,
            self.runtime,
            file_name
        ]

        ran_to_completion = True

        # Create a timer to watch for timeouts
        def timeout_func():
            ran_to_completion = False
            try:
                subprocess.call(['docker', 'rm', '-f', docker_name])
            except:
                pass
        timer = threading.Timer(self.timeout, timeout_func)
        timer.start()

        # Run the docker test command in a new process
        runner = subprocess.Popen(
            stdin=input_file,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = runner.communicate()

        # We're done with everything, stop the timer
        timer.cancel()

    """
    Take a submission and turn the submission text into a file we can run
    against docker
    """
    def prepare_submission(submission):
        fp = tempfile.TemporaryFile()
        fp.write(submission.submission_text)
        fp.seek(0)
        return fp
