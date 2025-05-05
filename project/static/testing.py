import firebase_admin
from firebase_admin import credentials, auth
import pyrebase
from datetime import *

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

cred = credentials.Certificate('project/credentials.json')
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

def get_first_name_with_uid(uid):
    keys1 = db.child("users").get()
    for key1 in keys1:
        user_id = list(key1.val().keys())[0]
        if(user_id == uid):
            keys2 = db.child("users").child(key1.key()).get()
            for key2 in keys2:
                return key2.val()['firstname']

def get_last_name_with_uid(uid):
    keys1 = db.child("users").get()
    for key1 in keys1:
        user_id = list(key1.val().keys())[0]
        if(user_id == uid):
            keys2 = db.child("users").child(key1.key()).get()
            for key2 in keys2:
                return key2.val()['lastname']

def get_email_with_uid(uid):
    keys1 = db.child("users").get()
    for key1 in keys1:
        user_id = list(key1.val().keys())[0]
        if(user_id == uid):
            keys2 = db.child("users").child(key1.key()).get()
            for key2 in keys2:
                return key2.val()['email']
            
def get_value_with_uid_key(uid, key):
    keys1 = db.child("users").get()
    for key1 in keys1:
        user_id = list(key1.val().keys())[0]
        if(user_id == uid):
            keys2 = db.child("users").child(key1.key()).get()
            for key2 in keys2:
                return key2.val()[key]


def change_item_with_uid(uid, itemkey, itemvalue):
    keys1 = db.child("users").get()
    for key1 in keys1:
        user_id = list(key1.val().keys())[0]
        if(user_id == uid):
            keys2 = db.child("users").child(key1.key()).get()
            for key2 in keys2:
                db.child("users").child(key1.key()).child(key2.key()).update({itemkey:itemvalue})

def add_item_with_uid(uid, itemkey, itemvalue):
    keys1 = db.child("users").get()
    for key1 in keys1:
        user_id = list(key1.val().keys())[0]
        if(user_id == uid):
            keys2 = db.child("users").child(key1.key()).get()
            for key2 in keys2:
                db.child("users").child(key1.key()).child(key2.key()).update({itemkey:itemvalue})

#add_item_with_uid("TIPjcipciuX8iFDew5YxR16h54H3", 'subject', ['math', 'english'])
#change_email_with_uid("TIPjcipciuX8iFDew5YxR16h54H3")

#get_first_name_with_uid("TIPjcipciuX8iFDew5YxR16h54H3")

# ans = input("Are you a new user? [y/n]")

# if ans == "y":
#     user, info = signup()
#     #print("User UID:", user['localId'])
#     data = {user['localId']:{"firstname":info[0], "lastname":info[1], "email":info[2]}}
#     db.child("users").push(data)
# else:
#     user = login()
#     #print("User UID:", user['localId'])
#     info = fetch_account_details()

# #info = [firstname, lastname, email]
# print(f"Hello {info[0]} {info[1]}")


# decision = input("What would you like to do?\n")

# if(decision == "delete"):
#     ars = input("Are you sure? [y/n] ")
#     if(ars == "y"):
#         delete_account_db()
#         delete_user(user['localId'])

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
   
#print(search_for_users_with_tags(get_value_with_uid_key('110209026888438200235', 'subject')))
# result = search_for_users_with_tags(['tutor'])
# print(result)

# now = datetime.now()
# print(now.astimezone().tzinfo)

# keys1 = db.child("users").get()
# for key1 in keys1:
#     user_id = list(key1.val().keys())[0]
#     if(user_id == "TIPjcipciuX8iFDew5YxR16h54H3"):
#         keys2 = db.child("users").child(key1.key()).get()
#         for key2 in keys2:
#             print(db.child("users").child(key1.key()).child(key2.key()).get().val())