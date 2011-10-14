#!/usr/bin/python

import os
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
	
	try:
		dong.config = json.load(open(CONFIG, 'r'))
		
	except ValueError, e:
		print 'Error parsing configuration:', e
		sys.exit(1)
		
	for i in dong.config['modules'].items():
		dong.modules[i[0]] = i[1]
		dong.commands[i[1]['command']] = i[0]
		__import__(i[1]['file'])

	
class DB:
	def __init__(self):
		if os.path.exists(dong.config['database']):
			self.cx = sqlite.connect(dong.config['database'], isolation_level=None)
			self.cu = self.cx.cursor()
		else:
			print "Database not found, quitting."
			sys.exit(1)


class TelnetConnector:
	def __init__(self):
		self.tn = None
	
	def connect(self):
		self.tn = telnetlib.Telnet(dong.config['host'], 7777)
		self.tn.read_until(" connected)")
		self.write("connect %s %s" % (dong.config['username'], dong.config['password']))
		if dong.config['first_command']:
			self.write(dong.config['first_command'])

	def write(self, str):
		if self.tn:
			self.tn.write(str + '\n')
		else:
			print 'No running telnet connection.'


class Processor:
	def __init__(self, con):
		self.con = con
	
	def parser(self):
		buf = self.con.read_until('\n')
		line = buf.split(" ", 3)
		
		# This makes sure Donginger does not catch what he says
		if line[0] == dong.config['bot_objnum'] and line[1] != dong.config['bot_objnum']:
			cmd = line[2]
			args = line[3]
			if cmd in dong.commands.keys():
				self.dispatch(cmd, args)
				
	def dispatch(self, cmd, args):
		pass
	

if __name__ == '__main__':
	print "Starting up..."
	
	dong = Dong()
	parseConf()
	con = TelnetConnector()
	db = DB()

	while True:
		try:
			proc.Parser()
			time.sleep(0.5)
		except: raise