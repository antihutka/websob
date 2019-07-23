import MySQLdb

def with_cursor(infun):
  def outfun(*args, **kwargs):
    wdb = args[0]
    db = MySQLdb.connect(host=wdb.host, user=wdb.user, passwd=wdb.passwd, db=wdb.db, charset='utf8')
    try:
      with db as cur:
        #cur = db.cursor()
        cur.execute('SET NAMES utf8mb4')
        ret = infun(cur, *args, **kwargs)
        db.commit()
        return ret
    finally:
      db.close()
  return outfun

class WebsobDB:
  def __init__(self, dbconfig):
    self.db = dbconfig['Database']
    self.host = dbconfig['Host']
    self.user = dbconfig['User']
    self.passwd = dbconfig['Password']

  @with_cursor
  def get_name(cur, self):
    cur.execute("SELECT username_id, username FROM usernames WHERE lastused IS NULL ORDER BY RAND() LIMIT 1 FOR UPDATE")
    uid, unm = cur.fetchone()
    cur.execute("UPDATE usernames SET lastused=CURRENT_TIMESTAMP() WHERE username_id=%s", (uid,))
    return uid,unm

  @with_cursor
  def log_message(cur, self, userid, msgtext):
    cur.execute("INSERT INTO messages (username_id, message_text) VALUES (%s, %s)", (userid, msgtext))

  @with_cursor
  def log_login(cur, self, userid, address):
    cur.execute("INSERT INTO logins (username_id, client_ip) VALUES (%s, %s)", (userid, address))
