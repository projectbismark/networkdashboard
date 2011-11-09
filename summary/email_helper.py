import smtplib

def send_email(sender,receivers,message):

	smtpObj = smtplib.SMTP('smtp.gmail.com')
	
smtpObj.sendmail(sender, receivers, message)         
	


