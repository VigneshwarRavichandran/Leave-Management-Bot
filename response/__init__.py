from datetime import date
from helper import *
from database import UserDb

db = UserDb()

def get_date(req, username, leave_limit):
  leave_type = req['queryResult']['outputContexts'][0]['parameters']['Leave_type']
  
  if req['queryResult']['parameters']['date-period'] == '':
    leave_date = req['queryResult']['outputContexts'][3]['parameters']['date']
    leave_date = leave_date[0:10]
    leave_taken = db.user_leave(username)
    if leave_taken[0] < leave_limit:
      leave_remaining = (leave_limit - leave_taken[0]) - 1
      email_msg = "{0} has requested for a {1} leave on {2}.".format(username, leave_type, leave_date)
      send_email(email_msg)
      if leave_type == 'sick':
        return [{"text": { "text": [ "Your leave request on {0} is send for approval. Your available leave is {1}. Take care of your health".format(leave_date, leave_remaining) ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "Your leave request on {0} is send for approval. Your available leave is {1}. Take care of your health.".format(leave_date, leave_remaining) ] } } ]
      elif leave_type == 'casual':
        return [{"text": { "text": [ "Your leave request on {0} is send for approval. Your available leave is {1}. Have a good time!".format(leave_date, leave_remaining) ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "Your leave request on {0} is send for approval. Your available leave is {1}. Have a good time!".format(leave_date, leave_remaining) ] } } ]
      return [{"text": { "text": [ "Your leave request on {0} is send for approval. Your available leave is {1}.".format(leave_date, leave_remaining) ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "Your leave request on {0} is send for approval. Your available leave is {1}.".format(leave_date, leave_remaining) ] } } ]
    return [{"text": { "text": [ "Sorry! No leaves are left for you"] }, "platform": "TELEGRAM" }, { "text": { "text": [ "Sorry! No leaves are left for you"] } } ]
  
  elif req['queryResult']['parameters']['date'] == '':
    start_date = req['queryResult']['outputContexts'][0]['parameters']['date-period']['startDate']
    end_date = req['queryResult']['outputContexts'][0]['parameters']['date-period']['endDate']
    start_date = start_date[0:10]
    end_date = end_date[0:10]
    leave_days = (date(int(start_date[0:4]), int(start_date[5:7]), int(start_date[8:10])) - date(int(end_date[0:4]), int(end_date[5:7]), int(end_date[8:10]))).days
    leave_taken = db.user_leave(username)
    if leave_taken[0] + leave_days > leave_limit:
      return [{"text": { "text": [ 'Sorry! No sufficient leaves are left for you' ] }, "platform": "TELEGRAM" }, { "text": { "text": [ 'Sorry! No sufficient leaves are left for you' ] } } ]
    email_msg = "{0} has requested for a {1} leave from {2} to {3}.".format(username, leave_type, start_date, end_date)
    send_email(email_msg)
    leave_remaining = (leave_limit - leave_taken[0]) - 1
    if leave_type == 'sick':
      return [{"text": { "text": [ "Your leave request from {0} to {1} is send for approval. Your available leave is {2}. Take care of your health.".format(start_date, end_date, leave_remaining) ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "Your leave request from {0} to {1} is send for approval. Your available leave is {2}. Take care of your health.".format(start_date, end_date, leave_remaining) ] } } ]
    elif leave_type == 'casual':
      return [{"text": { "text": [ "Your leave request from {0} to {1} is send for approval. Your available leave is {2}. Have a good time!".format(start_date, end_date, leave_remaining) ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "Your leave request from {0} to {1} is send for approval. Your available leave is {2}. Have a good time !".format(start_date, end_date, leave_remaining) ] } } ]
    return [{"text": { "text": [ "Your leave request from {0} to {1} is send for approval. Your available leave is {2}.".format(start_date, end_date, leave_remaining) ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "Your leave request from {0} to {1} is send for approval. Your available leave is {2}.".format(start_date, end_date, leave_remaining) ] } } ]
  
  else:
    return [{"text": { "text": [ "Please mention your leave dates" ] }, "platform": "TELEGRAM" }, { "text": { "text": [ "Please mention your leave dates" ] } } ]