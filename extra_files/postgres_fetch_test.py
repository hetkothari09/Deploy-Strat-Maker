import psycopg2
from flask_sqlalchemy import SQLAlchemy

conn = psycopg2.connect(
    database="gpt_prompt-responses",
    user="postgres",
    password="root",
    host="localhost"
)

cursor = conn.cursor()

cursor.execute("SELECT * FROM user1_data")

result = cursor.fetchall()

print(f"User: {result[0][1]}, \nassistant: {result[0][2]}")
