
import sys
from sqlalchemy import create_engine

class Db(object):
	pass

db = Db()

def parse_conf():
	db.config = {}
	
	try:
		db.config = json.load(open(CONFIG))
		
	except ValueError, e:
		print 'Error parsing configuration:', e
		sys.exit(1)


class Database:
	def __init__(self):
		self.con = None
		parse_conf()
		
	def create_engine(self):
		if db.config['engine'] == 'sqlite':
			self.con = create_engine("sqlite:///%s" % db.config['sqlite_file'])
			
		if not self.con.execute("select 1").scalar():
			print 'Connection to DB failed.'
			sys.exit(1)
			
	