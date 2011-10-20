
import sys
import json
from random import randrange

# SQLAlchemy imports
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql import select

class Database:
	def __init__(self):
		self.db_config = 'conf/database.conf'
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
		
		table_name = table_def[0]
		table_data = table_def[1]
		
		args = [table_name, self.metadata]
		constraints = []
		
		# First column is always 'id'
		args.append(Column('id', Integer, primary_key=True))
		
		for col in table_data.items():
			col_name = col[0]
			type = col[1]
			
			if col_name == "constraints":
				cons_col, cons_type = type.items()[0]
				if cons_type == "unique":
					constraints.append(UniqueConstraint(cons_col))

			else:
				if type == 'integer':
					type = Integer()
				elif type == 'string':
					type = String()

				args.append(Column(col_name, type))
				
		# Constraints need to be defined after columns
		if constraints:
			args.append(*constraints)
				
		self.tables[table_name] = Table(*args)

	def insert(self, table, data):
		ins = self.tables[table].insert()
		ins.execute(data)

	def delete(self, table, where):
		st = self.tables[table].delete(self.tables[table].c.id == where[1])
		self.session.execute(st)
		self.session.commit()

	def delete_by_name(self, table, where):
		st = self.tables[table].delete(self.tables[table].c.name == where[1])
		self.session.execute(st)
		self.session.commit()

	def get_random_row(self, table):
		count = self.session.query(self.tables[table]).count()
		rand = randrange(0, count)
		row = self.session.query(self.tables[table])[rand]
		return row
	
	def update(self, table, where, value):
		
		# I should probably ditch SQLAlchemy
		try:
			table = self.tables[table]
			where_field = getattr(table.c, where[0])
			where_value = where[1]
			value_field = getattr(table.c, value[0])
			
			table.update().where(where_field == where_value).values(value_field = value[1])
		except Exception, e:
			print 'Failed UPDATE:', e
		
		
		
		
