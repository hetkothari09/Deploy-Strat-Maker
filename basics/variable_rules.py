from flask import Flask, render_template
from markupsafe import escape

app = Flask(__name__)


@app.route("/")
def show_html():
    return render_template('index.html')


@app.route("/user/<username>")
def show_user_profile(username):
    # used to show different profiles of users.
    return f"This is the profile of {escape(username)}"


@app.route("/id/<int:userid>")
def get_user_id(userid):
    # converts text type to integer type
    return f"This is the userid: {escape(userid)}"


@app.route("/path/<path:sub_path>")
def get_user_path(sub_path):
    # shows the path after the '/path'
    # the 'path' is also a converter type that acts similar to strings but also accepts front and back-slashes
    return f"This is the path of the user - {sub_path}"


# static folder is used to render and serve our files as it is to the user.
# accessed by using /static/file-name endpoint

# templates folder is used to render any html pages
# accessed by using render_template
