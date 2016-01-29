from flask import Flask, render_template, request, redirect, url_for, jsonify
from mongoengine import connect
from judge import Judge
from submission import Submission
import uuid

app = Flask(__name__)

connect('collatz')

judge = Judge()

@app.route("/")
def index():
    return render_template('submit.html')

@app.route("/submit",  methods=['POST'])
def submit():
    code = request.form['code']

    # Generate a unique ID for the submission
    id = str(uuid.uuid4())[:8]
    while Submission.objects(id=id).count() > 0:
        id = str(uuid.uuid4())[:8]

    # save the submission and submit it for judging
    submission = Submission(submission_text=code, id=id)
    submission.save()
    judge.submit(submission)

    return redirect(url_for('view_submission', id=id))

@app.route("/submission/<id>")
def view_submission(id):
    submission = Submission.objects(id=id).first()
    return submission.submission_text

@app.route("/submission/<id>.json")
def submission_json(id):
    submission = Submission.objects(id=id).first()
    data = {
        'id': submission.id,
        'status': submission.status,
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
