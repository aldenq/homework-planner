from flask import Flask, redirect, url_for, render_template
from pymongo import MongoClient

app = Flask(__name__)

#pymango setup
client = MongoClient()
users = client.users
classes = client.classes
assignments = client.assignments

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template("dashboard.html")

@app.route('/login', methods=['GET'])
def login():
    return render_template("login.html")

@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)