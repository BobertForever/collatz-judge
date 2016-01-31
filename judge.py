import tempfile
import os
import queue
import threading
import subprocess
import uuid
import shlex
from collatz import Collatz
from submission import Submission

"""
A judge is a test runner which takes a submission and enques it for
verification of correctness. In order to avoid malicious code absuing the host,
this runs in a docker container expected to be running. The actual judging
happens in a background thread and is interacted with via a queue.
"""
class Judge:

    docker_name = 'sandbox'
    runtime = 'python3'
    timeout = 30

    def __init__(self):
        self.queue = queue.Queue()
        self.collatz = Collatz()
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
        f = self.prepare_submission(submission)
        file_path = os.path.dirname(f.name)
        file_name = os.path.basename(f.name)

        # The judge now has the submission
        submission.status = Submission.RUNNING
        submission.save()

        # Setup the docker command we're going to run to test the submission
        docker_name = str(uuid.uuid4())
        docker_cmd = [
            'docker',
            'run',
            '--name="%s"' % docker_name,
            '-v',
            '%s:/judging_dir:ro' % os.getcwd(),
            '-w',
            '/judging_dir',
            '-a',
            'stdin',
            '-a',
            'stdout',
            '-i',
            self.docker_name,
            self.runtime,
            f.name
        ]

        # Generate a test
        test_in, test_out = self.collatz.generate_tests()
        test_in_file = tempfile.TemporaryFile()
        test_in_file.write(test_in.encode("UTF-8"))
        test_in_file.seek(0)

        ran_to_completion = [True]

        # Create a timer to watch for timeouts
        def timeout_func():
            ran_to_completion[0] = False
            try:
                subprocess.call(['docker', 'rm', '-f', docker_name])
            except:
                pass
        timer = threading.Timer(self.timeout, timeout_func)
        timer.start()

        # Run the docker test command in a new process
        runner = subprocess.Popen(
            shlex.split(' '.join(docker_cmd)),
            stdin=test_in_file,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = runner.communicate()

        # We're done with everything, stop the timer
        timer.cancel()
        f.close()
        os.remove(f.name)

        # Verify the program's output if it completed
        if ran_to_completion[0]:
            self.verify_output(submission, stdout.decode('ascii'), test_out)
        else:
            submission.status = Submission.TIMEOUT
            submission.save()

    """
    Take a submission and turn the submission text into a file we can run
    against docker
    """
    def prepare_submission(self, submission):
        fp = open('tmp.py', 'w+')
        fp.write(submission.submission_text)
        fp.seek(0)
        return fp

    """
    Verify the output of the program and update the submission with the status
    """
    def verify_output(self, submission, actual, expected):
        if actual == expected:
            submission.status = Submission.PASSED
        else:
            submission.status = Submission.FAILED
            submission.actual_out = actual
            submission.expected_out = expected

        submission.save()
