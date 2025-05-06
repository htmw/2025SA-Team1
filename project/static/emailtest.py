from email.message import EmailMessage
import ssl
import smtplib

email_sender = 'otherthanteam1schedule@gmail.com'
app_pw = 'wvjx ownt kajh qtwm'
email_receiver = 'funaverage57@gmail.com'

name = "hi"
othername = "hi2"
time = "12:00pm"

subject = 'You have a session soon!'
body = f"""
Hey {name},

You have a session with {othername} at {time} tomorrow!
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