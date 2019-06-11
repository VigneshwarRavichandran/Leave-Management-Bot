from datetime import date
from helper import *
from database import UserDb
import json
from datetime import date, datetime
import datetime
import requests

db = UserDb()

# Get the date or dates for the leave from the user
def get_date(req, username, leave_limit):
  leave_type = req['queryResult']['outputContexts'][0]['parameters']['leave_type']
  # Check whether the leave is for single day
  if req['queryResult']['parameters']['date-period'] == '':
    leave_date = req['queryResult']['outputContexts'][3]['parameters']['date']
    leave_date = leave_date[0:10]
    # Get the number of leaves taken by the user
    leave_taken = db.user_leave(username)
    # Check whether the user has exceeded the leave limit or not
    if leave_taken[0] < leave_limit:
      leave_remaining = (leave_limit - leave_taken[0]) - 1
      email_msg = "{0} has requested for a {1} leave on {2}.".format(username, leave_type, leave_date)
      # Forwarding the leave request through email
      send_email(email_msg)
      # Returns reponse based on the type of leave 
      if leave_type == 'sick':
        return [{"text": { "text": [ "Your leave request on {0} is send for approval. Your available leave is {1}. Take care of your health".format(leave_date, leave_remaining) ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "Your leave request on {0} is send for approval. Your available leave is {1}. Take care of your health.".format(leave_date, leave_remaining) ] } } ]
      elif leave_type == 'casual':
        return [{"text": { "text": [ "Your leave request on {0} is send for approval. Your available leave is {1}. Have a good time!".format(leave_date, leave_remaining) ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "Your leave request on {0} is send for approval. Your available leave is {1}. Have a good time!".format(leave_date, leave_remaining) ] } } ]
      return [{"text": { "text": [ "Your leave request on {0} is send for approval. Your available leave is {1}.".format(leave_date, leave_remaining) ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "Your leave request on {0} is send for approval. Your available leave is {1}.".format(leave_date, leave_remaining) ] } } ]
    return [{"text": { "text": [ "Sorry! No leaves are left for you"] }, "platform": "TELEGRAM" }, { "text": { "text": [ "Sorry! No leaves are left for you"] } } ]
  
  # Check whether the leave is for multiple days
  elif req['queryResult']['parameters']['date'] == '':
    start_date = req['queryResult']['outputContexts'][0]['parameters']['date-period']['startDate']
    end_date = req['queryResult']['outputContexts'][0]['parameters']['date-period']['endDate']
    start_date = start_date[0:10]
    end_date = end_date[0:10]
    leave_days = (date(int(start_date[0:4]), int(start_date[5:7]), int(start_date[8:10])) - date(int(end_date[0:4]), int(end_date[5:7]), int(end_date[8:10]))).days
    # Get the number of leaves taken by the user
    leave_taken = db.user_leave(username)
    # Check whether the user has exceeded the leave limit or not
    if leave_taken[0] + leave_days > leave_limit:
      return [{"text": { "text": [ 'Sorry! No sufficient leaves are left for you' ] }, "platform": "TELEGRAM" }, { "text": { "text": [ 'Sorry! No sufficient leaves are left for you' ] } } ]
    email_msg = "{0} has requested for a {1} leave from {2} to {3}.".format(username, leave_type, start_date, end_date)
    # Forwarding the leave request through email
    if background_process(email_msg):
      leave_remaining = (leave_limit - leave_taken[0]) - 1
      # Returns reponse based on the type of leave 
      if leave_type == 'sick':
        return [{"text": { "text": [ "Your leave request from {0} to {1} is send for approval. Your available leave is {2}. Take care of your health.".format(start_date, end_date, leave_remaining) ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "Your leave request from {0} to {1} is send for approval. Your available leave is {2}. Take care of your health.".format(start_date, end_date, leave_remaining) ] } } ]
      elif leave_type == 'casual':
        return [{"text": { "text": [ "Your leave request from {0} to {1} is send for approval. Your available leave is {2}. Have a good time!".format(start_date, end_date, leave_remaining) ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "Your leave request from {0} to {1} is send for approval. Your available leave is {2}. Have a good time !".format(start_date, end_date, leave_remaining) ] } } ]
      return [{"text": { "text": [ "Your leave request from {0} to {1} is send for approval. Your available leave is {2}.".format(start_date, end_date, leave_remaining) ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "Your leave request from {0} to {1} is send for approval. Your available leave is {2}.".format(start_date, end_date, leave_remaining) ] } } ]
  
  else:
    return [{"text": { "text": [ "Please mention your leave dates" ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "Please mention your leave dates" ] } } ]

# Get the upcoming holidays
def get_leave():
  req = requests.get('https://date.nager.at/api/v1/get/AU/2019')
  data = req.json()
  for index in range(0, len(data)-1):
    start_date = data[index]['date']
    end_date = data[index+1]['date']
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    # Get th next holiday from the current date
    if (start_date <= date.today() <= end_date):
          return [{"text": { "text": [ "On {0} due to {1}.".format(data[index+1]['date'], data[index+1]['localName']) ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "On {0} due to {1}".format(data[index+1]['date'], data[index+1]['localName']) ] } } ]

# Creating a event in the google calender
def create_event(req):
  event_date = req['queryResult']['parameters']['event_date']
  event_start_time = req['queryResult']['parameters']['starttime']
  event_end_time = req['queryResult']['parameters']['endtime']
  output_contexts = req['queryResult']['outputContexts']
  event_attendees = None
  # Get event_attendees for the meeting
  for output_context in output_contexts:
    event_name = output_context['name'].split('/')
    if event_name[len(event_name)-1] == 'create_event-followup':
      event_attendees = output_context['parameters']['attendees']
  email_ids = []
  for event_attendee in event_attendees:
    email_id = db.get_email(event_attendee)
    email_ids.append(email_id[0])
  # Check whether there is a meeting exist already on the same date and time
  exist = meeting_exist(event_date, event_start_time, event_end_time)
  if exist:
    return [{"text": { "text": [ "Already a meeting is organised on {0} from {1} to {2}. Do you like to a have a alternate date and time ?".format(exist[0], exist[1], exist[2]) ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "Already a meeting is organised on {0} from {1} to {2}. Do you like to a have a alternate date and time ?".format(exist[0], exist[1], exist[2]) ] } } ]
  create_meeting(event_date, event_start_time, event_end_time, email_ids, event_attendees)
  return [{"text": { "text": [ "The meeting is arranged successfully" ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "The meeting is arranged successfully" ] } } ]

# Deleting a event in the google calender
def delete_event(req):
  event_date = req['queryResult']['parameters']['event_date']
  event_start_time = req['queryResult']['parameters']['starttime']
  event_end_time = req['queryResult']['parameters']['endtime']
  # Get the event_id if the event exists
  event_id = find_meeting(event_date, event_start_time, event_end_time)
  if event_id:
    # Delete the event using the event_id
    delete_meeting(event_id)
    return [{"text": { "text": [ "The meeting is cancelled successfully" ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "The meeting is cancelled successfully" ] } } ]
  return [{"text": { "text": [ "There is no meeting on the mentioned date and time" ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "There is no meeting on the mentioned date and time" ] } } ]

# Get the details about the event to be rescheduled
def get_reschedule_event(req):
  event_date = req['queryResult']['parameters']['prev_date']
  event_start_time = req['queryResult']['parameters']['prev_starttime']
  event_end_time = req['queryResult']['parameters']['prev_endtime']
  # Get the event_id if the event exists
  event_id = find_meeting(event_date, event_start_time, event_end_time)
  if event_id:
    return [{"text": { "text": [ "Mention the reschedule date and time" ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "Mention the reschedule date and time " ] } } ]
  return [{"text": { "text": [ "There is no meeting on the mentioned date and time" ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "There is no meeting on the mentioned date and time" ] } } ]

# Reschedule the event to mention date and time
def reschedule_event(req):
  original_date = req['queryResult']['outputContexts'][0]['parameters']['prev_date']
  original_start_time = req['queryResult']['outputContexts'][0]['parameters']['prev_starttime']
  original_end_time = req['queryResult']['outputContexts'][0]['parameters']['prev_endtime']
  reschedule_date = req['queryResult']['outputContexts'][0]['parameters']['next_date']
  reschedule_start_time = req['queryResult']['outputContexts'][0]['parameters']['next_starttime']
  reschedule_end_time = req['queryResult']['outputContexts'][0]['parameters']['next_endtime']
  # Get the details about the event to be rescheduled
  event_id = find_meeting(original_date, original_start_time, original_end_time)
  # Check whether there is event in the reschedule date and time
  exist = meeting_exist(reschedule_date, reschedule_start_time, reschedule_end_time)
  if exist:
    return [{"text": { "text": [ "Already a meeting is oraganised on {0} from {1} to {2}".format(exist[0], exist[1], exist[2]) ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "Already a meeting is oraganised on {0} from {1} to {2}".format(exist[0], exist[1], exist[2]) ] } } ]
  # Reschedule the event with event_id and event credentials
  reschedule_meeting(reschedule_date, reschedule_start_time, reschedule_end_time, event_id)
  return [{"text": { "text": [ "The meeting is rescheduled successfully" ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "The meeting is rescheduled successfully" ] } } ]