from __future__ import print_function
import smtplib
from email.mime.text import MIMEText
from redis import Redis
from rq import Queue, get_current_job
from googleapiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
import datetime
from datetime import datetime
from datetimerange import DateTimeRange

# Queue initialisation
q = Queue(connection=Redis())
q.empty()

def background_process(email_msg):
	result = q.enqueue(send_email, email_msg)
	return True

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

def create_meeting(event_date, event_start_time, event_end_time, email_ids, event_attendees):
	SCOPES = 'https://www.googleapis.com/auth/calendar'
	store = file.Storage('storage.json')
	creds = store.get()
	if not creds or creds.invalid:
			flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
			creds = tools.run_flow(flow, store)
	service = discovery.build('calendar', 'v3', http=creds.authorize(Http()))
	start_time = event_date[0:11]+event_start_time[11:19]+'+05:30'
	end_time = event_date[0:11]+event_end_time[11:19]+'+05:30'
	event_details = {
		'summary': 'Meeting',
		'start':  { 'dateTime': start_time },
		'end':    { 'dateTime': end_time },
		'attendees': [],
	}
	for index in range(0,len(event_attendees)):
		(event_details['attendees'].append({ 'email': email_ids[index], 'displayName': event_attendees[index]}))
	service.events().insert(calendarId='primary', sendNotifications=True, body=event_details).execute()

def meeting_exist(event_date, event_start_time, event_end_time):
	SCOPES = 'https://www.googleapis.com/auth/calendar'
	store = file.Storage('storage.json')
	creds = store.get()
	if not creds or creds.invalid:
			flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
			creds = tools.run_flow(flow, store)
	service = discovery.build('calendar', 'v3', http=creds.authorize(Http()))
	start_time = event_date[0:11]+event_start_time[11:19]+'+05:30'
	end_time = event_date[0:11]+event_end_time[11:19]+'+05:30'
	page_token = None
	while True:
		now = datetime.utcnow().isoformat() + 'Z'
		events = service.events().list(calendarId='primary', timeMin=now, pageToken=page_token).execute()
		for event in events['items']:
			time_range = DateTimeRange(event['start']['dateTime'][0:19],  event['end']['dateTime'][0:19])
			if start_time[0:19] in time_range or end_time[0:19] in time_range:
				if (start_time[0:19] == event['end']['dateTime'][0:19]) or (end_time[0:19] == event['start']['dateTime'][0:19]):
					return False
				exist_date = event['start']['dateTime']
				exist_start = event['start']['dateTime']
				exist_end = event['end']['dateTime']
				return [exist_date[0:10], exist_start[11:16], exist_end[11:16]]
		page_token = events.get('nextPageToken')
		if not page_token:
			break
		return False

def find_meeting(event_date, event_start_time, event_end_time):
	SCOPES = 'https://www.googleapis.com/auth/calendar'
	store = file.Storage('storage.json')
	creds = store.get()
	if not creds or creds.invalid:
			flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
			creds = tools.run_flow(flow, store)
	service = discovery.build('calendar', 'v3', http=creds.authorize(Http()))
	start_time = event_date[0:11]+event_start_time[11:19]+'+05:30'
	end_time = event_date[0:11]+event_end_time[11:19]+'+05:30'
	page_token = None
	while True:
		now = datetime.utcnow().isoformat() + 'Z'
		events = service.events().list(calendarId='primary', timeMin=now, pageToken=page_token).execute()
		for event in events['items']:
			if (start_time[0:19] == event['start']['dateTime'][0:19]) and (end_time[0:19] == event['end']['dateTime'][0:19]):
				return event['id']
		page_token = events.get('nextPageToken')
		if not page_token:
			break
		return False

def delete_meeting(event_id):
	SCOPES = 'https://www.googleapis.com/auth/calendar'
	store = file.Storage('storage.json')
	creds = store.get()
	if not creds or creds.invalid:
			flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
			creds = tools.run_flow(flow, store)
	service = discovery.build('calendar', 'v3', http=creds.authorize(Http()))
	service.events().delete(calendarId='primary', eventId=event_id).execute()

def reschedule_meeting(reschedule_date, reschedule_start_time, reschedule_end_time, event_id):
	SCOPES = 'https://www.googleapis.com/auth/calendar'
	store = file.Storage('storage.json')
	creds = store.get()
	if not creds or creds.invalid:
			flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
			creds = tools.run_flow(flow, store)
	service = discovery.build('calendar', 'v3', http=creds.authorize(Http()))
	start_time = reschedule_date[0:11]+reschedule_start_time[11:19]+'+05:30'
	end_time = reschedule_date[0:11]+reschedule_end_time[11:19]+'+05:30'
	event_details = {
		'summary': 'Meeting',
		'start':  { 'dateTime': start_time },
		'end':    { 'dateTime': end_time },
	}
	service.events().patch(calendarId='primary', eventId=event_id, sendNotifications=True, body=event_details).execute()