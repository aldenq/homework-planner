import os
from bson.objectid import ObjectId
from flask import Flask, redirect, url_for, render_template, request, flash, session
from pymongo import MongoClient
from flask_bcrypt import Bcrypt

app = Flask(__name__)
# app.secret_key = os.urandom(12)
app.secret_key = 'funny_key'

#Bcrypt setup
bcrypt = Bcrypt(app)

#pymango setup
client = MongoClient(f"mongodb+srv://heroku:{os.environ.get('PASSWORD')}@cluster0.2lvxa.mongodb.net/Cluster0?retryWrites=true&w=majority")

db = client.homework_planner
users = db.users
classes = db.classes
assignments = db.assignments

# -- HELPERS --
def logged_in():
    return session.get('username') and session.get('password')
def current_user():
    found_user = users.find_one({
        'username':session.get('username'),
        'password':session.get('password')
    })
    return found_user

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

# DASHBOARD
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if logged_in():
        user = current_user()
        user_classes = list(classes.find({'user_id':user['_id']}))
        for c in user_classes:
            print(f"Class: {c['_id']}")
            found_assignments = assignments.find({'class_id':c['_id']})
            c['assignments'] = []
            c['assignments'].extend(found_assignments)
            for a in list(found_assignments.clone()):
                print(f"\tassignment: {a['_id']}, c-id: {a['class_id']}")
        return render_template("dashboard.html", user=user, classes=user_classes)
    else:
        return redirect(url_for('login'))

# CLASSES
@app.route('/classes/new', methods=['POST'])
def class_new():
    if logged_in():
        form_data = {
            'name':request.form.get('name'),
            'description':request.form.get('description'),
            'color':request.form.get('color'),
            'user_id':current_user()['_id']
        }
        classes.insert_one(form_data)
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/classes/delete/<id>')
def class_delete(id):
    if logged_in():
        assignments.delete_many({'class_id':ObjectId(id)})
        classes.delete_one({'_id':ObjectId(id)})
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))


# ASSIGNMENTS
@app.route('/assignments/new/<class_id>', methods=['POST'])
def assignment_new(class_id):
    if logged_in():
        form_data = {
            'name':request.form.get('name'),
            'description':request.form.get('description'),
            'time':request.form.get('time'),
            'date':request.form.get('date'),
            'class_id':ObjectId(class_id)
        }
        assignments.insert_one(form_data)
        print(f"New Assignment id: {class_id}")

        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/assignments/delete/<id>', methods=['GET'])
def assignment_delete(id):
    if logged_in():
        assignments.delete_one({'_id':ObjectId(id)})
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))


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
            #add data to session
            session['username'] = found_user['username']
            session['password'] = found_user['password']
            flash('Found User', 'success')
            return redirect(url_for('dashboard'))
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
        return redirect(url_for("signup"))
    else:
        # store new user
        form_data['password'] = bcrypt.generate_password_hash(form_data['password'])
        users.insert_one(form_data)

        #add data to session
        session['username'] = form_data['username']
        session['password'] = form_data['password']
        flash('Successfully created user', 'success')

        return redirect(url_for("dashboard"))


if __name__ == '__main__':
    app.run(debug=True)