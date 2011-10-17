#!/usr/bin/python

import os
import re
import sys
import json
import telnetlib
import sqlite3 as sqlite

sys.path += ['plugins']

CONFIG = 'donginger.conf'

class Dong(object):
	pass

def parseConf():
	dong.modules = {}
	dong.commands = {}
	dong.plugins = {}
	dong.db_tables = {}
	
	try:
		dong.config = json.load(open(CONFIG))
		
	except ValueError, e:
		print 'Error parsing configuration:', e
		sys.exit(1)
		
	for i in dong.config['modules'].items():
		dong.modules[i[0]] = i[1]
		
		# Create a list of all the callbacks in that module
		for call in i[1]['callbacks'].items():
			dong.commands[call[0]] = [i[0], call[1]]
			
		# Create a list of all needed SQL tables
		for table in i[1]['db_tables'].items():
			dong.db_tables[table[0]] = table[1]

		# tee hee
		plug_entry = getattr(__import__(i[1]['file']),i[1]['file'].capitalize())
		dong.plugins[i[0]] = plug_entry(i[0], dong)

	
class DB:
	def __init__(self):
		if os.path.exists(dong.config['database']):
			self.cx = sqlite.connect(dong.config['database'], isolation_level=None)
			self.cu = self.cx.cursor()
		else:
			self.cx = sqlite.connect(dong.config['database'], isolation_level=None)
			self.cu = self.cx.cursor()
			
			


class TelnetConnector:
	def __init__(self):
		self.tn = None
	
	def connect(self):
		self.tn = telnetlib.Telnet(dong.config['host'], 7777)
		self.read_until(" connected)")
		self.write("connect %s %s" % (dong.config['username'], dong.config['password']))
		if dong.config['first_command']:
			self.write(dong.config['first_command'])

	def write(self, str):
		if self.tn:
			self.tn.write(str + '\n')
		else:
			print 'No running telnet connection.'
			
	def read_until(self, str):
		if self.tn:
			return self.tn.read_until(str)
		else:
			print 'No running telnet connection.'		


class Processor:
	def __init__(self):
		self.ansi_pat = re.compile('\033\[[0-9;]+m')
		
	def stripANSI(self, str):
		return self.ansipat.sub('', txt)
	
	def parser(self):
		buf = con.read_until('\n')
		buf = self.stripANSI(buf)
		line = buf.split(" ", 3)
		
		# This makes sure Donginger does not catch what he says
		if line[0] == dong.config['bot_objnum'] and line[1] != dong.config['bot_objnum']:
			cmd = line[2]
			args = line[3]
			if cmd in dong.commands.keys():
				self.dispatch(dong.commands[cmd][0], dong.commands[cmd][1], args)
				
	def dispatch(self, plugin, callback, args):
		dong.plugins[plugin](callback)(args)
	

if __name__ == '__main__':
	print "Starting up..."
	
	dong = Dong()
	parseConf()
	dong.db = DB()
	con = TelnetConnector()
	proc = Processor()

	while True:
		try:
			proc.parser()
			time.sleep(0.5)
		except: raise