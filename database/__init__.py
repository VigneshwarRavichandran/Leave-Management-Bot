import MySQLdb

class UserDb():
  def __init__(self):
    self.host = 'localhost'
    self.user = 'root'
    self.passwd = '1998'
    self.db = 'leave_management'
    self.conn = None

  def db_connect(self):
    try:
      self.conn = MySQLdb.connect(host= self.host, user = self.user, passwd = self.passwd, db = self.db)
      cur = self.conn.cursor()
      return cur
    except:
      return None

  def user_leave(self, username):
    cur = self.db_connect()
    if cur:
      cur.execute("SELECT leave_days FROM user_details WHERE name = '{0}'".format(username))
      return(cur.fetchone())
    raise ConnectionError()

  def get_email(self, event_attendee):
    cur = self.db_connect()
    if cur:
      cur.execute("SELECT email FROM user_details WHERE name = '{0}'".format(event_attendee))
      return(cur.fetchone())
    raise ConnectionError()

  def close(self):
    self.conn.close()
    