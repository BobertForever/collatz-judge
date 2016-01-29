from flask import Flask, render_template
from mongoengine import connect
from judge import Judge

app = Flask(__name__)

connect('collatz')

judge = Judge()

@app.route("/")
def hello():
    return render_template('submit.html')

if __name__ == "__main__":
    app.run(debug=True)
