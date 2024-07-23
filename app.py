import json
from flask import Flask, render_template, request, url_for, redirect
import os
from dotenv import load_dotenv
from openai import OpenAI
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from datetime import datetime

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

db = SQLAlchemy(app)


@app.route("/")
def user_profiles():
    return render_template("index.html")


def create_db_table(table_name):
    class Table(db.Model):
        __tablename__ = table_name
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

    return Table
    render_template('db.html')


# @app.route("/submit", methods=["GET", "POST"])
# def submit():
#     if request.method == 'POST':
#         prompt = request.form.get("prompt_data")
#         responses = request.form.get("result")
#         table = Table(prompt, responses)
#         db.session.add(table)
#         db.session.commit()
#         return redirect(url_for('submit'))
#     return render_template('submit.html')


def create_endpoints(username, table_model):
    # @app.route(f"/{username}", methods=['POST', 'GET'])
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


# @app.route("/user2", methods=["GET", "POST"])
# def user2():
#     if request.method == 'POST':
#         prompt_data = request.form["prompt_data"]
#         response = client.chat.completions.create(
#             model=model,
#             messages=[
#                 {'role': 'system', 'content': 'You are an assistant designed to extract key indicators and trading '
#                                               'conditions from a given paragraph of information and generate a JSON'
#                                               ' file in a specific format structure.'},
#                 {'role': 'user', 'content': prompt_data}
#             ],
#             max_tokens=600,
#             temperature=0.4
#         )
#         result = response.choices[0].message.content
#
#         table = Table(prompt=prompt_data, responses=result)
#         db.session.add(table)
#         db.session.commit()
#
#         return redirect(url_for('user2', result=result))
#     result = request.args.get('result')
#     return render_template('interface.html', result=result)
#
#
# @app.route("/user3")
# def user3():
#     return "This is the page of user3"


@app.route("/navigate_pages", methods=['POST'])
def navigate_pages():
    selected_users = request.form.get("users")
    if selected_users == 'user1':
        return redirect(url_for('user1'))
    elif selected_users == 'user2':
        return redirect(url_for('user2'))
    elif selected_users == 'user3':
        return redirect(url_for('user3'))
    else:
        return redirect(url_for('/'))


# def show_database(username):
#     table_name = f"{username}_data"
#     with current_app.app_context():
#         query = f"SELECT * FROM {table_name}"
#         cursor.execute(query)
#         result2 = cursor.fetchall()
#         return render_template('interface.html', result=result2)


user1Table = create_db_table('user1_data')
user2Table = create_db_table('user2_data')
user3Table = create_db_table('user3_data')


create_endpoints('user1', user1Table)
create_endpoints('user2', user2Table)
create_endpoints('user3', user3Table)


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


# show_database('user1')
# show_database('user2')
# show_database('user3')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

