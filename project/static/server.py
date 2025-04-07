from firebase import firebase
from flask import Flask, render_template, request, redirect
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load variables from .env
load_dotenv()
db=os.environ.get("DB")
firebase = firebase.FirebaseApplication(db, None)
app = Flask(__name__,template_folder='../templates')  # Flask constructor

@app.route('/')
def home():
  result = firebase.get('/test', None)
  tutorResults = firebase.get('/tutor', None)
  return render_template('index.html',events=result,tutors=tutorResults)

@app.route('/timeTest')
def timetest():
  output=""
  result = firebase.get('/test', None)
  keys =result.keys()
  for i in keys:

     start_time_object =datetime.strptime(result[i]["StartTime"],"%Y-%m-%dT%H:%M")
     end_time_object =datetime.strptime(result[i]["EndTime"],"%Y-%m-%dT%H:%M")
     time_diff=(end_time_object-start_time_object)
     
     if time_diff<timedelta(0):
        output+=str("Negative")
     else:
       output+=str("Positive")
     output+="_____\n"
 
  return str(output)


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
    name = userdata["name"]
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
    firebase.post("/test", new_data)
    return "Event Added!"
  else:
    return "Sorry, there was an error."

@app.route('/submitTutor', methods=['GET', 'POST'])
def submitTutor():
  if request.method == 'POST' and len(dict(request.form)) > 0:
    userdata = dict(request.form)
    name = userdata["name"]

    new_data = {"Name": name}
    firebase.post("/tutor", new_data)
    return "Tutor Added!"
  else:
    return "Sorry, there was an error."

app.run(debug=True)