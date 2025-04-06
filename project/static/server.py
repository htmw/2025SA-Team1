from firebase import firebase
from flask import Flask, render_template, request, redirect
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

from firebase_admin import credentials, auth, initialize_app
import pyrebase

# Load variables from .env
#load_dotenv()
#db=os.environ.get("DB")

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

cred = credentials.Certificate('2025SA-Team1\credentials.json')
fb=initialize_app(cred)
firebase = pyrebase.initialize_app(firebaseConfig)
authpy = firebase.auth()
db = firebase.database()

#firebase = firebase.FirebaseApplication(db, None)
app = Flask(__name__,template_folder='../templates',static_folder="../static")  # Flask constructor

@app.route('/')
def home():
  result = db.child("events").get()
  tutorResults = db.child("tutors").get()
  return render_template('index.html',events=result,tutors=tutorResults)




@app.route('/addTutor')
def index():
    return render_template('tutor.html')

@app.route('/error/<errorcode>')
def error_code(errorcode):
   return f"Error: {errorcode}"
   


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

app.run(debug=True)