
import sys
import json

# SQLAlchemy imports
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Integer, String, MetaData

class Database:
	def __init__(self):
		self.db_config = 'database.conf'
		self.con = None
		self.base = None
		self.metadata = None
		self.session = None
		
		self.tables = {}
		self.config = {}
		self.parse_conf()
		
	def parse_conf(self):
		try:
			self.config = json.load(open(self.db_config))
			
		except ValueError, e:
			print "Error parsing configuration %s:" % self.db_config, e
			sys.exit(1)
		
	def create_engine(self):
		if self.config['engine'] == 'sqlite':
			self.con = create_engine("sqlite:///%s" % self.config['sqlite_file'])
			self.metadata = MetaData()
			self.metadata.bind = self.con
			
	def create_session(self):
		Session = sessionmaker(bind=self.con)
		self.session = Session()
	
	def test_connection(self):
		if not self.con.execute("select 1").scalar():
			print 'Connection to DB failed.'
			sys.exit(1)
			
	def create_table(self, table_def):
		"""Oh god, this is so ugly."""
		
		table = table_def[1]
		for i in table.items():
			if i[1] == 'string':
				table[i[0]] = String()
			elif i[1] == 'integer':
				table[i[0]] = Integer()
			
		self.tables[table_def[0]] = Table(table_def[0], self.metadata, Column('id', Integer, primary_key=True),
					  *(Column(col, ctype) for (col, ctype) in table.items()))
		
	def insert(self, table, data):
		ins = self.tables[table].insert()
		ins.execute(data)
		
		
		
		
