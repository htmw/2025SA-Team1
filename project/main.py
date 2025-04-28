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
user = None
 
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
                return redirect(url_for("homepage"))
            except Exception as e:
                print("error has occured: ", e)
                return redirect(url_for("error_code", ecode=400))          
    return render_template('signup.html')
 
@app.route('/homepage')
def homepage():
    return render_template('homepage.html', user_name = give_user_first_name())

@app.route('/error/<ecode>')
def error_code(ecode):
   return f"Error: {ecode}"
 
@app.route('/schedule')
def schedule():
    return render_template('schedule.html')
 
@app.route('/viewSchedule')
def viewSchedule():
    events= db.child("events").get()
    return render_template('viewSchedule.html',res=events)
 
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
    name = userdata["student-name"]
    tutor = userdata["tutor"]
    startTime = userdata["sTime"]
    endTime = userdata["eTime"]
    subject = userdata["subject"]
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
       
def give_user_first_name():
    global user
    if user:
        users = db.child("users").get()
        for user1 in users.each():
            user_dict = user1.val()
            #print(user_dict)
            user_id = list(user1.val().keys())[0]

            if(user_id == user['localId']):
                return user_dict[user_id]['firstname']

def search_for_users_with_tags(tags, user_ids = []):
   users = db.child("users").get()
   filter_users = []
   if(len(tags) > 0):
       for user in users:
        user_id = list(user.val().keys())[0]
        if(user_id in user_ids or len(user_ids) == 0):
            for key in user.val()[user_id].keys():
                if(user.val()[user_id][key].lower() == tags[0].lower()):
                    filter_users.append(user_id)
       tags.remove(tags[0])
       return search_for_users_with_tags(tags, filter_users)
   else:
      user_ids = list(dict.fromkeys(user_ids))
      return user_ids

app.run(debug=True)
 
