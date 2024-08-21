from flask import Flask, request, url_for, flash, redirect, render_template

app = Flask(__name__)

SECRET_KEY = 'many random bytes'
app.secret_key = 'many random bytes'


@app.get('/')
def cred():
    flash('Test message', 'info')
    return render_template('alertTest.html')


if __name__ == '__main__':
    app.run(debug=True)