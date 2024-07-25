from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p> Hello world </p>"


'''
command:
flask --app basicFunc run

flask --app basicFunc run --debug  (used if you want the changes to update in real-time)
'''
