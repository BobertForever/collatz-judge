from flask import Flask, render_template, request, redirect, url_for, jsonify, Markup
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
    return render_template('submission.html', submission=submission)

def newline_to_br(text):
    tmp = ""
    for line in text.split('\n'):
        tmp += Markup.escape(line) + Markup('<br />')
    return tmp

@app.route("/submission/<id>/out")
def view_submission_output(id):
    submission = Submission.objects(id=id).first()
    expected = newline_to_br(submission.expected_out)
    actual = newline_to_br(submission.actual_out)
    return render_template('output.html', expected=expected, actual=actual, id=submission.id)

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
