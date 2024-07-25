import json
from flask import Flask, render_template, request, url_for, redirect, current_app
import os
from dotenv import load_dotenv
from openai import OpenAI
from flask_sqlalchemy import SQLAlchemy
import psycopg2

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

        def __init__(self, prompt, responses, history):
            self.prompt = prompt
            self.responses = responses
            self.history = history
    return Table

def create_endpoints(username, table_model):
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
                                                  'conditions from a given paragraph of information and generate a '
                                                  'JSON file in a specific format structure.'},
                    *history
                ],
                max_tokens=600,
                temperature=0.4
            )
            result = response.choices[0].message.content

            history.append({"role": "assistant", "content": result})

            create_table = table_model(prompt=prompt_data, responses=result, history=history)
            db.session.add(create_table)
            db.session.commit()

            return redirect(url_for(f'{username}', result=result, history=json.dumps(history)))
        result = request.args.get('result')
        history = request.args.get('history', '[]')
        return render_template('interface.html', result=result, username=username, history=history)

    user_endpoint.__name__ = f"{username}"
    app.route(f"/{username}", methods=['POST', 'GET'])(user_endpoint)


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


user1Table = create_db_table('user1_data')
user2Table = create_db_table('user2_data')
user3Table = create_db_table('user3_data')

create_endpoints('user1', user1Table)
create_endpoints('user2', user2Table)
create_endpoints('user3', user3Table)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)











# ::::::::::::
#
#
# <!doctype html>
# <html lang="en">
# <head>
#   <meta charset="utf-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1">
#     <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.rtl.min.css" integrity="sha384-dpuaG1suU0eT09tx5plTaGMLBsfDLzUCCUXOY2j/LSvXYuG6Bqs43ALlhIqAJVRb" crossorigin="anonymous">
#
#     <title>JSON-maker</title>
#    <style>
#     .container {
#       display: flex;
#       justify-content: center;
#       align-items: center;
#       height: 70vh;
#     }
#     .box {
#       padding: 20px;
#       border: 1px solid #ccc;
#       border-radius: 5px;
#       margin: 10px;
#     }
#     .box2 {
#       padding: 20px;
#       border: 1px solid #ccc;
#       border-radius: 5px;
#       margin: 10px;
#     }
#     .result-box {
#       height: 50vh;
#       overflow-y: auto;
#     }
#     .result-box2 {
#       height: 50vh;
#       overflow-y: auto;
#       margin-top:-40px;
#     }
#   </style>
# </head>
# <body>
#     <a href="/">
#     <h1 class="text-center">JSON-maker</h1>
#     </a>
#     <!--    <form action="/user1" method="POST" class="d-flex justify-content-center align-items-center" style="height: 50vh;">-->
#     <div class="container">
#     <form action="/{{username}}" method="POST" class="box">
#         <div class="mb-3">
#             <label for="prompt_data" class="form-label">User</label>
#             <textarea name="prompt_data"  placeholder="Enter your prompt here" name="prompt_data" id="prompt_data" required> </textarea>
#             <input type="hidden" name="history" value="{{ history }}">
#         </div>
#             <button type="submit" class="btn btn-primary">Submit</button>
#     </form>
#     <form action="/dbshow/{{username}}" method="get">
#     <button class="btn btn-primary">Show Database</button>
#     </form>
#
#
# <!--     <input type="file"> {{result}}</input>-->
#     {% if result %}
#     <div class="box result-box">
#         <label class="form-label">Assistant</label>
#         <div class="result" id="result">{{result}}</div>
#     </div>
#     {% endif %}
#     </div>
#
#     <div class="box2 result-box2">
#         <label class="form-label"><h5>Chat History</h5></label>
#         <div class="history">
# <!--            {% for chat in chat_history %}-->
# <!--            <div class="chat-entry">-->
# <!--                <strong>{{username}}:</strong> {{ chat.prompt }}<br>-->
# <!--                <strong>Assistant:</strong> {{ chat.responses }}<br><br>-->
# <!--    &lt;!&ndash;        <strong>History:</strong> {{ chat.history }}<br><br>&ndash;&gt;-->
# <!--            </div>-->
# <!--            {% endfor %}-->
#         </div>
#     </div>
#
#   <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
#
# </body>
# </html>
#







# ------------------------------------------------------------------------------- #


# ::::::::----------------------------------:::::::::::::
#
#
# <!--            {% set myList = [] %}-->
# <!--            {% if result %}-->
# <!--                {% for item in chat_history %}-->
# <!--                    {% if loop.last %}-->
# <!--                        {% set _ = myList.append(item.prompt) %}-->
# <!--                        {% set _ = myList.append(item.responses) %}-->
# <!--                    {% endif %}-->
# <!--                {% endfor %}-->
# <!--            {% else %}-->
# <!--                <strong>{{username}}:</strong> <br>-->
# <!--                <strong>Assistant:</strong> <br><br>-->
# <!--            {% endif %}-->
#
# <!--            {% for x in myList %}-->
# <!--                {% if not flag %}-->
# <!--                    <strong>{{username}}:</strong> {{myList[loop.index-1]}} <br>-->
# <!--                    <strong>Assistant:</strong> {{myList[loop.index]}} <br><br>-->
# <!--                {% else %}-->
# <!--                    <strong>{{username}}:</strong> {{myList[loop.index]}} <br>-->
# <!--                    <strong>Assistant:</strong> {{myList[loop.index+1]}} <br><br>-->
# <!--                {% endif %}-->
# <!--            {% endfor %}-->
# <!--            {% set flag = 1 %}-->
# <!--&lt;!&ndash;        {{ myList }}        &ndash;&gt;-->