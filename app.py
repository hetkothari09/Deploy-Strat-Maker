import json
from flask import Flask, render_template, request, url_for, redirect
import os
from dotenv import load_dotenv
from openai import OpenAI
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from datetime import datetime
from flask_bcrypt import Bcrypt

conn = psycopg2.connect(
    database="gpt_prompt-responses",
    user="postgres",
    password="root",
    host="localhost"
)
cursor = conn.cursor()

load_dotenv()
model = os.getenv("MODEL")
api_key = os.getenv("API_KEY")
client = OpenAI(api_key=api_key)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:root@localhost:5432/gpt_prompt-responses'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class UserCreds(db.Model):
    __tablename__ = 'user_creds'
    sNo = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password


class Table(db.Model):
    __tablename__ = 'generic_table'
    sNo = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.String(5000))
    responses = db.Column(db.String(8000))
    history = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, prompt, responses, history, timestamp):
        self.prompt = prompt
        self.responses = responses
        self.history = history
        self.timestamp = timestamp


@app.route("/", methods=['POST', 'GET'])
def signup_page():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        unhashed_password = request.form.get("password")
        password = bcrypt.generate_password_hash(unhashed_password)
        # password = request.form.get("password")
        print(name, email, password)
        cred_table = UserCreds(name=name, email=email, password=password)
        db.session.add(cred_table)
        db.session.commit()
    return render_template('signup.html')


@app.route("/login", methods=["POST", "GET"])
def login_page():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        # unhashed_password = request.form.get("password")
        # password = bcrypt.generate_password_hash(unhashed_password)
        # print(password)
        password = request.form.get("password")
        # cursor.execute('SELECT password FROM public.user_creds WHERE email = %s', (email,))
        # result = cursor.fetchone()

        email_list = []
        cursor.execute('SELECT email from public.user_creds')
        emails = cursor.fetchall()
        for x in emails:
            email_list.append(x[0])

        pwd_list = []
        cursor.execute('SELECT password from public.user_creds')
        pwds = cursor.fetchall()
        for x in pwds:
            pwd_list.append(x[0])

        if email in email_list:
            if bcrypt.check_password_hash():
            # if password in pwd_list:
                return redirect('/user1')

    return render_template('login.html')


def create_endpoints(username, table_model):
    @app.route(f"/{username}", methods=['POST', 'GET'])
    def user_endpoint():
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

            history.append({"role": "assistant", "content": result})

            timestamp = datetime.now()

            create_table = table_model(prompt=prompt_data, responses=result, history=history, timestamp=timestamp)
            db.session.add(create_table)
            db.session.commit()

            return redirect(url_for(f'{username}', result=result, history=json.dumps(history)))
        result = request.args.get('result')
        history = request.args.get('history', '[]')
        chat_history = table_model.query.all()
        return render_template('interfaceTesting.html', result=result, username=username, history=history,
                               chat_history=chat_history, timestamp=(datetime.now()).strftime('%d-%m-%Y %H:%M:%S'))
    user_endpoint.__name__ = f"{username}"
    app.route(f"/{username}", methods=['POST', 'GET'])(user_endpoint)


@app.route('/dbshow/<username>', methods=["POST", "GET"])
def show_database(username):
    data_name = f'{username}_data'
    query = f"SELECT * FROM public.{data_name}"
    cursor.execute(query)
    result = cursor.fetchall()
    timestamp = datetime.now()

    output = []
    for row in result:
        output.append({'user': row[1], 'assistant': row[2], 'timestamp': row[4]})

    return render_template('db.html', output=output, username=username, timestamp=timestamp)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
