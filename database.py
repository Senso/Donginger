
import sys
import json

# SQLAlchemy imports
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData

class Database:
	def __init__(self):
		self.db_config = 'database.conf'
		self.con = None
		self.base = None
		self.metadata = None
		
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
	
	def test_connection(self):
		if not self.con.execute("select 1").scalar():
			print 'Connection to DB failed.'
			sys.exit(1)
			
	def create_table(self, table_def):
		"""Oh god, this is so ugly."""
		
		t_dict = {'__tablename__': table_def[0]}
		
		t_dict['id'] = Column(Integer, primary_key=True)
		for (col, data) in table_def[1].items():
			if data == 'string':
				t_dict[col] = Column(String)
			elif data == 'integer':
				t_dict[col] = Column(Integer)
		
		Base = declarative_base()
		table_obj = type(str(table_def[0].capitalize()), (Base,), t_dict)
				
		self.metadata.create_table(table_obj)
		


	
	
	
	
	
	