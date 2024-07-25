import json
from flask import Flask, render_template, request, url_for, redirect
import os
from dotenv import load_dotenv
from openai import OpenAI
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from datetime import datetime

# Connect to PostgreSQL
conn = psycopg2.connect(
    database="gpt_prompt-responses",
    user="postgres",
    password="root",
    host="localhost"
)
cursor = conn.cursor()

# Load environment variables
load_dotenv()
model = os.getenv("MODEL")
api_key = os.getenv("API_KEY")
client = OpenAI(api_key=api_key)

# Initialize Flask application
app = Flask(__name__)

# Configure SQLAlchemy for PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:root@localhost:5432/gpt_prompt-responses'
db = SQLAlchemy(app)

# Function to create SQLAlchemy table models
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

# List to store user names dynamically
users = []

# Function to create endpoints dynamically
def create_user_endpoint(username, table_model):
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
        return render_template('interface.html', result=result, username=username, history=history,
                               chat_history=chat_history, timestamp=(datetime.now()).strftime('%d-%m-%Y %H:%M:%S'))

    user_endpoint.__name__ = f"{username}"  # Set function name
    app.add_url_rule(f"/{username}", view_func=user_endpoint)  # Add rule to the application
    users.append(username)  # Add username to the list

# Endpoint to add new users
@app.route("/add_user", methods=['POST'])
def add_user():
    new_username = request.form.get("new_user")
    if new_username:
        create_user_endpoint(new_username, create_db_table(f'{new_username}_data'))
    return redirect(url_for('user_profiles'))

# Route for the main user profiles page
@app.route("/")
def user_profiles():
    return render_template("index.html", users=users)

# Route to display database entries for a specific user
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

# Ensure that Flask application is run only when this script is executed directly
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create all defined tables in the database
    app.run(debug=True)  # Start the Flask application in debug mode
