import os
from flask import Flask, redirect, url_for, render_template, request, flash
from pymongo import MongoClient
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = os.urandom(12)

#Bcrypt setup
bcrypt = Bcrypt(app)

#pymango setup
client = MongoClient()
db = client.homework_planner
users = db.users
classes = db.classes
assignments = db.assignments

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template("dashboard.html")

# LOGIN
@app.route('/login', methods=['GET'])
def login():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login_form():

    form_data = {
        'username': request.form.get('username'),
        'password': request.form.get('password')
    }

    found_user = users.find_one({'username':form_data['username']})
    if found_user:
        if bcrypt.check_password_hash(found_user['password'], form_data['password']):
            flash('Found User', 'success')
        else:
            flash('Password is Wrong', 'warning')
    else:
        flash('User not found', 'danger')

    return redirect(url_for("login"))


# SIGN UP
@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_form():

    form_data = {
        'username': request.form.get('username'),
        'password': request.form.get('password'),
        'name': request.form.get('name')
    }

    found_user = users.find_one({'username':form_data['username']})
    if found_user:
        flash('User exists', 'danger')
    else:
        flash('Successfully created user', 'success')

    return redirect(url_for("signup"))

if __name__ == '__main__':
    app.run(debug=True)