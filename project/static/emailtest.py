from email.message import EmailMessage
import ssl
import smtplib

email_sender = 'funaverage57@gmail.com'
app_pw = ''
email_receiver = 'justinriv326@gmail.com'

subject = 'Python Test'
body = """
Man this is crazy
you just got send an email by python code

brother isnt that insane

english fail

this statement is false

this message was indeed sent by bot.
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

print("end of file")