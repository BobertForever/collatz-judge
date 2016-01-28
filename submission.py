from mongoengine import *

class Submission(Document):
    WAITING = 'waiting'
    RUNNING = 'running'
    FINISHED = 'finished'

    id = StringField(required=True)
    submission_text = StringField(required=True)
    status = StringField(default=WAITING, required=True)
