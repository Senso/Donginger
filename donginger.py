#!/usr/bin/python

import sys
import json
import telnetlib
import sqlite3 as sqlite
from xml.etree.ElementTree import ElementTree

CONFIG = 'donginger.xml'
conf = {}

class Dong(object):
	pass

def parseConf():
	try:
		dong.config = json.load(CONFIG)
		
	except ValueError, e:
		print 'Error parsing configuration:', e
		sys.exit(1)
		
	for name, conf in dong.config['modules']:
		dong.modules[name] = conf
		dong.commands[conf['command']] = name
		
		
class DB:
	def __init__(self):
		if os.path.exists(conf['main_db']):
			self.cx = sqlite.connect(conf['main_db'], isolation_level=None)
			self.cu = self.cx.cursor()
		else:
			print "Database not found, quitting."
			sys.exit(1)
		
		
class TelnetConnector:
	def __init__(self):
		self.tn = None
	
	def connect(self):
		self.tn = telnetlib.Telnet(conf['host'], 7777)
		self.tn.read_until(" connected)")
		self.write("connect %s %s" % (conf['username'], conf['password']))
		if conf['first_command']:
			self.write(conf['first_command'])

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
		self.line = buf.split(" ", 3)
		
	

if __name__ == '__main__':
	print "Starting up..."
	
	dong = Dong()
	con = TelnetConnector()
	db = DB()

	while True:
		try:
			proc.Parser()
			time.sleep(0.5)
		except: raise