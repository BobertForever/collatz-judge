from mongoengine import *

class Submission(Document):
    WAITING = 'waiting'
    RUNNING = 'running'
    TIMEOUT = 'timeout'
    PASSED = 'passed'
    FAILED = 'failed'

    id = StringField(required=True, primary_key=True)
    submission_text = StringField(required=True)
    status = StringField(default=WAITING, required=True)
    actual_out = StringField()
    expected_out = StringField()
