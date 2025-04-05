import firebase_admin
from firebase_admin import credentials, auth
import pyrebase

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

cred = credentials.Certificate('credentials.json')
firebase_admin.initialize_app(cred)
firebase = pyrebase.initialize_app(firebaseConfig)
authpy = firebase.auth()
db = firebase.database()

def login():
    print("login...")
    em = input("Enter email: ")
    pw = input("Enter password: ")
    try:
        user = authpy.sign_in_with_email_and_password(em, pw)
        return user
    except Exception as e:
        print("an error has occured ", e)

def signup():
    print("Sign up...")
    em = input("Enter email: ")
    pw = input("Enter password: ")
    try:
        user = authpy.create_user_with_email_and_password(em, pw)
        info = enter_account_details(em)
        return user, info
    except Exception as e:
        print("error has occured: ", e)

def enter_account_details(email):
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    return [first_name, last_name, email]

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
        
ans = input("Are you a new user? [y/n]")

if ans == "y":
    user, info = signup()
    #print("User UID:", user['localId'])
    data = {user['localId']:{"firstname":info[0], "lastname":info[1], "email":info[2]}}
    db.child("users").push(data)
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