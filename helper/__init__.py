import smtplib
from email.mime.text import MIMEText

def send_email(email_msg):
	smtp_ssl_host = 'smtp.gmail.com'
	smtp_ssl_port = 465
	username = '16jecit119@gmail.com'
	password = 'user@123'
	sender = '16jecit119@gmail.com'
	# contents for the message

	msg = MIMEText(email_msg)
	msg['Subject'] = 'Leave Request'
	msg['From'] = sender
	msg['To'] = 'vigneshwarravichandran@zoho.com'
	# email connection establishment and execution
	server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
	server.login(username, password)
	server.sendmail(sender, 'vigneshwarravichandran@zoho.com', msg.as_string())
	server.quit()