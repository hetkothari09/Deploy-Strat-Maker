# from flask_sqlalchemy import SQLAlchemy
# import psycopg2
#
# conn = psycopg2.connect(
#     database="gpt_prompt-responses",
#     user="postgres",
#     password="root",
#     host="localhost"
# )
# cursor = conn.cursor()
#
# email_list = []
# cursor.execute('SELECT email FROM public.user_creds')
# emails = cursor.fetchall()
#
# for x in emails:
#     email_list.append(x)
#
# pwd_list = []
# cursor.execute('SELECT password FROM public.user_creds')
# pwds = cursor.fetchall()
#
# for x in pwds:
#     pwd_list.append(x)
#
#
# sample_email = 'het@gmail.com'
#
# if sample_email in email_list:
#     print("True")
# else:
#     print("False")
#
# print(email_list)
#
#

import psycopg2

conn = psycopg2.connect(
    database="gpt_prompt-responses",
    user="postgres",
    password="root",
    host="localhost"
)
cursor = conn.cursor()

email_list = []
cursor.execute('SELECT email FROM public.user_creds')
emails = cursor.fetchall()

for x in emails:
    email_list.append(x[0])

pwd_list = []
cursor.execute('SELECT password FROM public.user_creds')
pwds = cursor.fetchall()

for x in pwds:
    pwd_list.append(x[0])

sample_email = 'hok@gmail.com'

if sample_email in email_list:
    print("True")
else:
    print("False")


sample_pwd = r"\x24326224313224653658305878706939755a755963655132794249326554426c664e392f63444e59377a6e4d705536793361644d654844717768334f"

if sample_pwd in pwd_list:
    print("True")
else:
    print("False")

