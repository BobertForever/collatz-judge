from flask import Flask
from mongoengine import connect
from judge import Judge

app = Flask(__name__)

connect('collatz')

judge = Judge()

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run()
