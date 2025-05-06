import firebase_admin
from firebase_admin import credentials, auth
from _thread import *
import pyrebase
from flask import *
from datetime import datetime, timedelta
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import  Flow
from googleapiclient.discovery import build
import requests
import tzlocal
from email.message import EmailMessage
import ssl
import smtplib

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
timezone_abbr = tzlocal.get_localzone_name()


GOOGLE_CLIENT_ID = calendar_data['client_id']
GOOGLE_CLIENT_SECRET = calendar_data['client_secret']
CALENDAR_API = 'calendar'
API_VERSION = 'v3'
SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/calendar.readonly",
          "https://www.googleapis.com/auth/userinfo.email","openid"]

REDIRECT_URI = "http://localhost:5000/oauth2callback"

@app.route('/', methods=['GET', 'POST'])
def index():
    global user
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Handle email/password login as before...
 
        try:
            user = authpy.sign_in_with_email_and_password(username,password)
        except Exception as e:
            print("an error has occured ", e)
 
        if user:
            return redirect('/homepage')
    return render_template('index.html')
    
@app.route('/update-profile', methods=['GET', 'POST'])
def update_profile():
    print("updating profile...")
    if request.method == 'POST':
        email = session['userInfo']['email']
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        role = request.form.get('user-type')
        if(request.form.getlist('subjects')):
            subject = request.form.getlist('subjects')
        else:
            subject = request.form.getlist('subjects-needed')
        if(request.form.getlist("ages")):
            ages = request.form.getlist("ages")
        else:
            ages = request.form.getlist('student-age')
        print("Sign up...")
        print(session['userInfo']['id'])
        if(search_for_users_with_tags([email]) == []):
            try:
                data = {session['userInfo']['id']:{"firstname":firstname, "lastname":lastname, "email":email, "role":role, "subject":subject, "ages":ages}}
                db.child("users").push(data)
                return redirect(url_for("homepage"))
            except Exception as e:
                print("error has occured: ", e)
                return redirect(url_for("error_code", ecode=400))
        else:
            if(firstname):
                change_item_with_uid(session['userInfo']['id'], 'firstname', firstname)
            if(lastname):
                change_item_with_uid(session['userInfo']['id'], 'lastname', lastname)
            if(role):
                change_item_with_uid(session['userInfo']['id'], 'role', role)
            if(subject):
                change_item_with_uid(session['userInfo']['id'], 'subject', subject)
            if(ages):
                change_item_with_uid(session['userInfo']['id'], 'ages', ages)
            return redirect(url_for("homepage"))
    return render_template('profilePage.html')
    

# def signingup():
#     global user
#     if request.method == 'POST':
#         email = request.form.get('email')
#         password = request.form.get('password')
#         firstname = request.form.get('firstName')
#         lastname = request.form.get('lastName')
#         role = request.form.get('role')
#         if password == request.form.get('confirmPassword'):
#             print("Sign up...")
#             try:
#                 user = authpy.create_user_with_email_and_password(email, password)
#                 data = {user['localId']:{"firstname":firstname, "lastname":lastname, "email":email, "role":role}}
#                 db.child("users").push(data)
#                 return redirect(url_for("homepage"))
#             except Exception as e:
#                 print("error has occured: ", e)
#                 return redirect(url_for("error_code", ecode=400))          
#     return render_template('signup.html')
 
# @app.route('/create-account-google', methods=['GET', 'POST'])


@app.route('/homepage')
def homepage():
    session['role'] = get_value_with_uid_key(session['userInfo']['id'], 'role')
    return render_template('homepage.html', user_name = give_user_first_name())

@app.route('/error/<ecode>')
def error_code(ecode):
   return f"Error: {ecode}"
 

@app.route('/schedule')
def schedule():
    search_terms = ['tutor']
    subjects = get_value_with_uid_key(session["userInfo"]['id'], "subject")
    for subject in subjects:
        search_terms.append(subject)
    tutors = search_for_users_with_tags(search_terms)
    names = []
    for tutor in tutors:
        names.append(get_value_with_uid_key(tutor, 'firstname'))
    print(tutors)
    return render_template('schedule.html', tutors_list= tutors, names_list= names, role = session['role'])

'''
<label for="tutor">Select Tutor:</label>
          <select id="tutor" name="tutor" required>
            <option value="Sabrina">Sabrina</option>
            <option value="Justin">Justin</option>
          </select>
'''




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
    print(search_for_users_with_tags([session['userInfo']['email']]))
    if(search_for_users_with_tags([session['userInfo']['email']]) == []):
        print("new account")
        return redirect(url_for("update_profile"))
    print(session["userInfo"] )

    return redirect(url_for("homepage"))


@app.route('/addTutor')
def addTutor():
    return render_template('addtutor.html')

@app.route('/findTutor')
def findTutor():
    return render_template('findTutor.html')

@app.route('/submitFT', methods=['GET', 'POST'])
def submitFT():
    if request.method == 'POST' and len(dict(request.form)) > 0:
        userdata = dict(request.form)
        day = userdata['day']
        time = userdata['session_time']
        subject = userdata['subject']
        return search_for_users_with_tags(['tutor', day, time, subject], [])

 
#REWRITE THIS FOR NEW DATABASE FORMAT
@app.route('/submit', methods=['GET', 'POST'])
def submit():
  if request.method == 'POST' and len(dict(request.form)) > 0:
    userdata = dict(request.form)
    tutor = userdata["tutor"]
    startTime = f"{userdata["sTime"]}:00"
    endTime = f"{userdata["eTime"]}:00"
    print(startTime)
    print(endTime)
    start_time_object =datetime.strptime(startTime,"%Y-%m-%dT%H:%M:%S")
    end_time_object =datetime.strptime(endTime,"%Y-%m-%dT%H:%M:%S")
    time_diff=(end_time_object-start_time_object)
 
    try:
        if time_diff<timedelta(0):
            raise Exception("End time is before the Start time")
    except:
        return redirect('/error/400')
    try:
        creds = Credentials(**session['credentials'])
        service = build('calendar', 'v3', credentials=creds)
        event = {
        'summary': 'Flask Test Event',
        'location': 'Online',
        'description': 'Event created with Flask and Google Calendar API',
        'start': {
            'dateTime': f"{startTime}",
            'timeZone': f'{timezone_abbr}',
        },
        'end': {
            'dateTime': f"{endTime}",
            'timeZone': f'{timezone_abbr}',
            },
        }

        created_event = service.events().insert(calendarId='primary', body=event).execute()
    except Exception as e:
        print(e)
        return redirect('/error/400')
    
    new_data = {"StudentID": session['userInfo']['id'] ,"TutorID": tutor,"StartTime":startTime,"EndTime":endTime, "NotificationFlag": False}
    db.child("events").push(new_data)    

    return redirect(url_for("calendar_page"))
  else:
    return "Sorry, there was an error."
 
@app.route('/tutorsubmit', methods=['GET','POST'])
def tutor_set_avaliability():
  if request.method == 'POST' and len(dict(request.form)) > 0:
    userdata = dict(request.form)
    startTime = f"{userdata["aStart"]}:00"
    endTime = f"{userdata["aEnd"]}:00"
    change_item_with_uid(session['userInfo']['id'], 'avaliability', [startTime, endTime])
    return redirect(url_for("calendar_page"))



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


def give_user_first_name():
    users = db.child("users").get()
    for user1 in users.each():
        user_dict = user1.val()
        #print(user_dict)
        user_id = list(user1.val().keys())[0]

        if(user_id == session['userInfo']['id']):
            return user_dict[user_id]['firstname']

def change_item_with_uid(uid, itemkey, itemvalue):
    keys1 = db.child("users").get()
    for key1 in keys1:
        user_id = list(key1.val().keys())[0]
        if(user_id == uid):
            keys2 = db.child("users").child(key1.key()).get()
            for key2 in keys2:
                db.child("users").child(key1.key()).child(key2.key()).update({itemkey:itemvalue})

def get_value_with_uid_key(uid, key):
    keys1 = db.child("users").get()
    for key1 in keys1:
        user_id = list(key1.val().keys())[0]
        if(user_id == uid):
            keys2 = db.child("users").child(key1.key()).get()
            for key2 in keys2:
                return key2.val()[key]

def search_for_users_with_tags(tags, user_ids = []):
   users = db.child("users").get()
   filter_users = []
   if(len(tags) > 0):
       for user in users:
        user_id = list(user.val().keys())[0]
        if(user_id in user_ids or len(user_ids) == 0):
            for key in user.val()[user_id].keys():
                if(not isinstance(user.val()[user_id][key], list) and user.val()[user_id][key].lower() == tags[0].lower()):
                    filter_users.append(user_id)
                elif(isinstance(user.val()[user_id][key], list)):
                    for subkey in user.val()[user_id][key]:
                        if(subkey.lower() == tags[0].lower()):
                            filter_users.append(user_id)
       tags.remove(tags[0])
       return search_for_users_with_tags(tags, filter_users)
   else:
      user_ids = list(dict.fromkeys(user_ids))
      return user_ids

def get_first_name_with_uid(uid):
    keys1 = db.child("users").get()
    for key1 in keys1:
        user_id = list(key1.val().keys())[0]
        if(user_id == uid):
            keys2 = db.child("users").child(key1.key()).get()
            for key2 in keys2:
                return key2.val()['firstname']

def get_email_with_uid(uid):
    keys1 = db.child("users").get()
    for key1 in keys1:
        user_id = list(key1.val().keys())[0]
        if(user_id == uid):
            keys2 = db.child("users").child(key1.key()).get()
            for key2 in keys2:
                return key2.val()['email']

def send_24_hour_email(personid, otherpersonid, time):
    email_sender = 'otherthanteam1schedule@gmail.com'
    app_pw = 'wvjx ownt kajh qtwm'
    email_receiver = get_email_with_uid(personid)

    subject = 'You have a session soon!'
    body = f"""
    Hey {get_first_name_with_uid(personid)},

    You have a session with {get_first_name_with_uid(otherpersonid)} at {time} tomorrow!
    """

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:
        smtp.login(email_sender, app_pw)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

    print("email send!")

def email_daemon():
    while(True):
        schedules = db.child("events").get()
        for schedule in schedules:
            start_time_object =datetime.strptime(schedule.val()['StartTime'],"%Y-%m-%dT%H:%M:%S")
            now_time_object =datetime.now()
            time_diff=(start_time_object - now_time_object)
            if time_diff<timedelta(1) and not schedule.val()['NotificationFlag']:
                for key in db.child("events").child(schedule.key()).get():
                    db.child("events").child(schedule.key()).update({"NotificationFlag":True})
                send_24_hour_email(schedule.val()['StudentID'], schedule.val()['TutorID'], start_time_object.strftime("%Y-%m-%d %H:%M:%S"))
                send_24_hour_email(schedule.val()['TutorID'], schedule.val()['StudentID'], start_time_object.strftime("%Y-%m-%d %H:%M:%S"))

start_new_thread(email_daemon, ())

app.run(debug=True)
 
