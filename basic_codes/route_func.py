# route function is used to route between different urls
from flask import Flask

app = Flask(__name__)


@app.route("/")
def index_page():
    return 'Index Page'


@app.route("/home")
def home_page():
    return 'Home Page'


