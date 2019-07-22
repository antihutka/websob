import sys
import MySQLdb
from configparser import ConfigParser
Config = ConfigParser()
Config.read(sys.argv[1])

db = MySQLdb.connect(host=Config.get('Database', 'Host'), user=Config.get('Database', 'User'), passwd=Config.get('Database', 'Password'), db=Config.get('Database', 'Database'), charset='utf8')
cur = db.cursor()
cur.execute('SET NAMES utf8mb4')

def isnew(n):
  cur.execute("SELECT COUNT(*) FROM usernames WHERE username=%s", (n,))
  r = cur.fetchone()[0]
  return (r == 0)

cnt = 0

def cmt():
  db.commit()
  print("%d new names" % cnt)

with open(sys.argv[2], 'r') as f:
  for line in f:
    if line.endswith('\n'):
      line = line[:-1]
      if isnew(line):
        print(line)
        cur.execute("INSERT INTO usernames (username) VALUES (%s)", (line,))
        cnt += 1
        if cnt % 100 == 0:
          cmt()
cmt()
