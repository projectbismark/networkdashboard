import smtplib
from email.mime.text import MIMEText

def send_email(sender,receivers,subject,message):

	smtpserver = 'smtp.gmail.com'
	AUTHREQUIRED = 1 
	smtpuser = "bismarkfeedback@gmail.com"
	smtppass = 'password89'
	
	RECIPIENTS = receivers
	SENDER = sender
	
	msg = MIMEText(message)
	msg['Subject'] = subject
	msg['From'] = sender
	msg['To'] = receivers[0]

	mailServer = smtplib.SMTP('smtp.gmail.com',587)

	mailServer.ehlo()
	mailServer.starttls()
	mailServer.ehlo()
	mailServer.login(smtpuser, smtppass)
	mailServer.sendmail(smtpuser,RECIPIENTS,msg.as_string())
	mailServer.close()

	


