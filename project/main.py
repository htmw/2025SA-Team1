import firebase_admin
from firebase_admin import credentials, auth
import pyrebase
from flask import *
from datetime import datetime, timedelta

firebaseConfig = {
  "apiKey": "AIzaSyDk7B6wLTh6yxRUcxoN2SmoI64ANUTBaeY",
  "authDomain": "scheduled-5b0e3.firebaseapp.com",
  "databaseURL": "https://scheduled-5b0e3-default-rtdb.firebaseio.com",
  "projectId": "scheduled-5b0e3",
  "storageBucket": "scheduled-5b0e3.firebasestorage.app",
  "messagingSenderId": "384090122282",
  "appId": "1:384090122282:web:cd754ea0539bdf246cfb53",
  "measurementId": "G-1M901DBRZ3"
}

cred = credentials.Certificate('firebase/credentials.json')
firebase_admin.initialize_app(cred)
firebase = pyrebase.initialize_app(firebaseConfig)
app = Flask(__name__,template_folder='templates')
authpy = firebase.auth()
db = firebase.database()
user = None
info = None

@app.route('/', methods=['GET', 'POST'])
def index():
    global user, info
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Handle email/password login as before...
        user = login(username, password)
        info = fetch_account_details()
    return render_template('index.html')

@app.route('/create-account', methods=['GET', 'POST'])
def signingup():
    global user, info
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        firstname = request.form.get('firstName')
        lastname = request.form.get('lastName')
        role = request.form.get('role')
        if password == request.form.get('confirmPassword'):
            user = signup(email, password, firstname, lastname, role)
            info = fetch_account_details()
    return render_template('signup.html')


@app.route('/schedule')
def home():
  result = db.child("events").get()
  tutorResults = db.child("tutors").get()
  return render_template('schedule.html',events=result,tutors=tutorResults)

@app.route('/addTutor')
def addTutor():
    return render_template('tutor.html')

#REWORTE THIS FOR NEW DATABASE FORMAT
@app.route('/submit', methods=['GET', 'POST'])
def submit():
  if request.method == 'POST' and len(dict(request.form)) > 0:
    userdata = dict(request.form)
    name = userdata["student-name"]
    tutor = userdata["tutor"]
    startTime = userdata["sTime"]
    endTime = userdata["eTime"]

    start_time_object =datetime.strptime(startTime,"%Y-%m-%dT%H:%M")
    end_time_object =datetime.strptime(endTime,"%Y-%m-%dT%H:%M")
    time_diff=(end_time_object-start_time_object)
 
    try:
        if time_diff<timedelta(0):
            raise Exception("End time is before the Start time")
    except :
        return redirect('/error/400')
    
    new_data = {"StudentName": name, "TutorName": tutor,"StartTime":startTime,"EndTime":endTime}
    db.child("events").push(new_data)
    return "Event Added!"
  else:
    return "Sorry, there was an error."

@app.route('/submitTutor', methods=['GET', 'POST'])
def submitTutor():
  if request.method == 'POST' and len(dict(request.form)) > 0:
    userdata = dict(request.form)
    name = userdata["name"]

    new_data = {"Name": name}
    db.child("tutors").push(new_data)
    return "Tutor Added!"
  else:
    return "Sorry, there was an error."

def login(em, pw):
    print("login...")
    try:
        user = authpy.sign_in_with_email_and_password(em, pw)
        print("successful")
        return user
    except Exception as e:
        print("an error has occured ", e)

def signup(em, pw, first_name, last_name, role):
    print("Sign up...")
    try:
        user = authpy.create_user_with_email_and_password(em, pw)
        data = {user['localId']:{"firstname":first_name, "lastname":last_name, "email":em, "role":role}}
        db.child("users").push(data)
        return user
    except Exception as e:
        print("error has occured: ", e)

def fetch_account_details():
    users = db.child("users").get()
    for user1 in users.each():
        user_dict = user1.val()
        #print(user_dict)
        user_id = list(user1.val().keys())[0]

        if(user_id == user['localId']):
            return [user_dict[user_id]['firstname'], user_dict[user_id]['lastname'], user_dict[user_id]['email']]

def delete_user(id):
    try:
        auth.delete_user(id)
    except Exception as e:
        print("error has occured: ", e)

def delete_account_db():
    keys = db.child("users").get()
    for key in keys:
        user_id = list(key.val().keys())[0]
        if(user_id == user['localId']):
            db.child("users").child(key.key()).remove()
        
app.run(debug=True)

'''ans = input("Are you a new user? [y/n]")

if ans == "y":
    user, info = signup()
    #print("User UID:", user['localId'])
else:
    user = login()
    #print("User UID:", user['localId'])
    info = fetch_account_details()

#info = [firstname, lastname, email]
print(f"Hello {info[0]} {info[1]}")


decision = input("What would you like to do?\n")

if(decision == "delete"):
    ars = input("Are you sure? [y/n] ")
    if(ars == "y"):
        delete_account_db()
        delete_user(user['localId'])
'''
'''
import firebase_admin
from firebase_admin import credentials, auth
 
app = Flask(__name__)
app.secret_key = 'your_secret_key'
 
# Initialize Firebase Admin SDK
cred = credentials.Certificate('path/to/your/firebase/credentials.json')
firebase_admin.initialize_app(cred)
 
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Handle email/password login as before...
 
    return render_template('index.html')
 
@app.route('/login_with_google', methods=['POST'])
def login_with_google():
    data = request.json
    user_id = data.get('uid')
    email = data.get('email')
 
    try:
        user = auth.get_user(user_id)
    except:
        user = auth.create_user(uid=user_id, email=email)
 
    session['user'] = email
    return jsonify({'success': True})
 
@app.route('/schedule')
def schedule():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('schedule.html')
 
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))
 
if __name__ == '__main__':
    app.run(debug=True)'''