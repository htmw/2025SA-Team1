import firebase_admin
from firebase_admin import credentials, auth
import pyrebase
from flask import *
from datetime import datetime, timedelta
import json
from google_auth_oauthlib.flow import  Flow
from googleapiclient.discovery import build
import requests

#FOR TESTING PURPOSES ONLY SHOULD NOT BE IN PRODUCTION CODE
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

with open('project\\firebaseConfig.json', 'r') as f:
    firebaseConfig = json.load(f)

with open('project\\calendarCred.json', 'r') as f:
    calendar_data = json.load(f)
calendar_data=calendar_data['web']
cred = credentials.Certificate('project\\credentials.json')
firebase_admin.initialize_app(cred)
firebase = pyrebase.initialize_app(firebaseConfig)
app = Flask(__name__,template_folder='templates')
app.secret_key = "1bc91f883a5737c0a5105cf2fa1130ce"

authpy = firebase.auth()
db = firebase.database()
user =None


GOOGLE_CLIENT_ID = calendar_data['client_id']
GOOGLE_CLIENT_SECRET = calendar_data['client_secret']
CALENDAR_API = 'calendar'
API_VERSION = 'v3'
SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/calendar.readonly",
          "https://www.googleapis.com/auth/userinfo.email","openid"]

REDIRECT_URI = "http://localhost:5000/oauth2callback"


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
    return render_template('schedule.html')

@app.route('/viewSchedule')
def viewSchedule():
    creds_data = session.get("credentials")
    if not creds_data:
        return redirect(url_for("authorize"))

    from google.oauth2.credentials import Credentials
    creds = Credentials(**creds_data)

    service = build("calendar", "v3", credentials=creds)
    events_result = service.events().list(calendarId="primary", maxResults=10, singleEvents=True,
                                          orderBy="startTime").execute()
    events = events_result.get("items", [])

    output = "<h1>Upcoming Events</h1><ul>"
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        output += f"<li>{start} - {event['summary']}</li>"
    output += "</ul>"
    return output


@app.route("/calendar")
def calendar_page():
    userEmail = session['userInfo']['email']
    return render_template("viewSchedule.html", email=userEmail)


@app.route("/authorize")
def authorize():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=SCOPES,
    )
    flow.redirect_uri = REDIRECT_URI
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true')
    return redirect(auth_url)

@app.route("/oauth2callback")
def oauth2callback():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=SCOPES,
    )
    flow.redirect_uri = REDIRECT_URI
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes
    }
    headers = {
    'Authorization': f'Bearer {credentials.token}'
    }
    response =  requests.get(
        'https://www.googleapis.com/oauth2/v1/userinfo?alt=json',
        headers=headers
    ).json()
    session["userInfo"] = response

    print(session["userInfo"] )

    return redirect(url_for("viewSchedule"))


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
    subject = userdata["subject"]
    print(subject)
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

