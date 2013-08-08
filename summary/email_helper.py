import smtplib
from email.mime.text import MIMEText
from networkdashboard.summary.models import *

def send_email(has,sender,message):

	details = Devicedetails.objects.filter(hashkey=has)[0]

	displayURL = "http://networkdashboard.org/displayDevice/" + has
	
	message = "URL: " + displayURL + "\n" + "email: " + sender + "\n\n"  + message

	subject = "feedback: " + details.deviceid

	receivers = ['bismarkfeedback@gmail.com','bismark-core@projectbismark.net']

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

	


