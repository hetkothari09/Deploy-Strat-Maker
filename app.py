from flask import Flask, render_template, request, url_for, redirect, abort, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv
from datetime import datetime
import json
import psycopg2
from openai import OpenAI
import jwt

load_dotenv()
model = os.getenv("MODEL")
api_key = os.getenv("API_KEY")
client = OpenAI(api_key=api_key)
google_client_id = os.getenv("GOOGLE_CLIENT_ID")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:root@localhost:5432/gpt_prompt-responses'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

conn = psycopg2.connect(
    database="gpt_prompt-responses",
    user="postgres",
    password="root",
    host="localhost"
)
cursor = conn.cursor()


class UserCreds(db.Model):
    __tablename__ = 'user_creds'
    sNo = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=True)

    def __init__(self, name, email, password=None):
        self.name = name
        self.email = email
        self.password = password


# creates db table based on the username
def create_db_table(table_name):
    class Table(db.Model):
        __tablename__ = table_name
        sNo = db.Column(db.Integer, primary_key=True)
        prompt = db.Column(db.String(5000))
        responses = db.Column(db.String(8000))
        history = db.Column(db.JSON)
        timestamp = db.Column(db.DateTime, default=datetime.now())

        __table_args__ = {'extend_existing': True}

        def __init__(self, prompt, responses, history, timestamp):
            self.prompt = prompt
            self.responses = responses
            self.history = history
            self.timestamp = timestamp

    return Table


@app.route("/", methods=['POST', 'GET'])
def signup_page():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        unhashed_password = request.form.get("password")

        # google_data = request.json
        # gname = google_data.get('given_name')
        # print(gname)

        password = bcrypt.generate_password_hash(unhashed_password).decode('utf-8')

        cred_table = UserCreds(name=name, email=email, password=password)
        db.session.add(cred_table)
        db.session.commit()

        # Create user-specific table
        create_user_table(name)

        return redirect(url_for('login_page'))
    return render_template('signup.html')


# @app.route("/google-signup", methods=['POST'])
# def google_signup():
#     data = request.json
#     email = data.get("email")
#     name = data.get("name")
#
#     user = UserCreds.query.filter_by(email=email).first()
#     if user:
#         return jsonify({"success": False, "message": "User already exists"}), 409
#
#     cred_table = UserCreds(name=name, email=email)
#     db.session.add(cred_table)
#     db.session.commit()
#
#     # Create user-specific table
#     create_user_table(name)
#
#     return jsonify({"success": True})


@app.route("/login", methods=["POST", "GET"])
def login_page():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = UserCreds.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            username = user.name
            return redirect(url_for('user_endpoint', username=username))
        else:
            return "Invalid credentials", 401

    return render_template('login.html')


# @app.route("/google-login", methods=['POST'])
# def google_login():
#     data = request.json
#     email = data.get("email")
#
#     user = UserCreds.query.filter_by(email=email).first()
#     if user:
#         return jsonify({"success": True})
#     else:
#         return jsonify({"success": False, "message": "User not found"}), 404


@app.route("/<username>", methods=['POST', 'GET'])
def user_endpoint(username):
    table_model = create_db_table(f'{username}_data')
    if request.method == 'POST':
        prompt_data = request.form["prompt_data"]
        history = request.form.get("history")
        if history:
            history = json.loads(history)
        else:
            history = []
        history.append({"role": "user", "content": prompt_data})

        response = client.chat.completions.create(
            model=model,
            messages=[
                {'role': 'system', 'content': 'You are an assistant designed to extract key indicators and trading '
                                              'conditions from a given paragraph of information and generate a JSON'
                                              ' file in a specific format structure.'},
                *history
            ],
            max_tokens=600,
            temperature=0.4
        )
        result = response.choices[0].message.content

        history.append({"role": 'assistant', "content": result})

        timestamp = datetime.now()

        create_table = table_model(prompt=prompt_data, responses=result, history=history, timestamp=timestamp)
        db.session.add(create_table)
        db.session.commit()

        return redirect(url_for('user_endpoint', username=username, result=result, history=json.dumps(history)))

    result = request.args.get('result')
    history = request.args.get('history', '[]')
    chat_history = table_model.query.all()
    return render_template('interfaceTesting.html', result=result, username=username, history=history,
                           chat_history=chat_history, timestamp=(datetime.now()).strftime('%d-%m-%Y %H:%M:%S'))


@app.route('/dbshow/<username>', methods=["POST", "GET"])
def show_database(username):
    data_name = f'{username}_data'
    query = f"SELECT * FROM public.{data_name}"
    cursor.execute(query)
    result = cursor.fetchall()
    timestamp = datetime.now()

    output = []
    for row in result:
        output.append({'prompt': row[1], 'responses': row[2], 'timestamp': row[4]})

    return render_template('db.html', output=output, username=username, timestamp=timestamp)


@app.route("/navigate_pages", methods=['POST'])
def navigate_pages():
    selected_users = request.form.get("users")
    return redirect(url_for('user_endpoint', username=selected_users))


def create_user_table(username):
    table_model = create_db_table(f'{username}_data')
    with app.app_context():
        db.create_all()


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


# @app.after_request
# def add_headers(response):
#     response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
#     response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
#     return response


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        existing_users = UserCreds.query.all()
        for user in existing_users:
            create_user_table(user.name)
    app.run(debug=True, port=5000, host='localhost')
