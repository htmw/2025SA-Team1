import firebase_admin
from firebase_admin import credentials, auth
import pyrebase
from flask import *
from datetime import datetime, timedelta
import json

with open('project/firebaseConfig.json', 'r') as f:
    firebaseConfig = json.load(f)

cred = credentials.Certificate('project/credentials.json')
firebase_admin.initialize_app(cred)
firebase = pyrebase.initialize_app(firebaseConfig)
app = Flask(__name__,template_folder='templates')
authpy = firebase.auth()
db = firebase.database()
user =None

@app.route('/', methods=['GET', 'POST'])
def index():
    token =None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Handle email/password login as before...

        try:
            token = authpy.sign_in_with_email_and_password(username,password)
        except Exception as e:
            print("an error has occured ", e)

        if token:
            return redirect('/schedule')
    return render_template('index.html')

@app.route('/create-account', methods=['GET', 'POST'])
def signingup():
    global user
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        firstname = request.form.get('firstName')
        lastname = request.form.get('lastName')
        role = request.form.get('role')
        if password == request.form.get('confirmPassword'):
            print("Sign up...")
            try:
                user = authpy.create_user_with_email_and_password(email, password)
                data = {user['localId']:{"firstname":firstname, "lastname":lastname, "email":email, "role":role}}
                db.child("users").push(data)
                return redirect(url_for("schedule"))
            except Exception as e:
                print("error has occured: ", e) 
                return redirect(url_for("error_code", ecode=400))           
    return render_template('signup.html')

@app.route('/error/<ecode>')
def error_code(ecode):
   return f"Error: {ecode}"

@app.route('/schedule')
def schedule():
  result = db.child("events").get()
  tutorResults = db.child("tutors").get()
  return render_template('schedule.html',events=result,tutors=tutorResults)

@app.route('/addTutor')
def addTutor():
    return render_template('tutor.html')

#REWRITE THIS FOR NEW DATABASE FORMAT
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
    except:
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

