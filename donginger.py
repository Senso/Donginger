#!/usr/bin/python

import sys
import telnetlib
import sqlite3 as sqlite
from xml.etree.ElementTree import ElementTree

CONFIG = 'donginger.xml'
conf = {}

def parseConf():
	global conf
	try:
		tree = ElementTree()
		tree.parse(CONFIG)

		conf['main_db'] = tree.find('database').text
		conf['username'] = tree.find('username').text
		conf['password'] = tree.find('password').text
		conf['host'] = tree.find('host').text
		conf['first_command'] = tree.find('first_command').text
		
		return conf
	except:
		print 'Error parsing configuration.'
		sys.exit(1)
		
		
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
		self.tn.write("connect %s %s\n" % (conf['username'], conf['password']))
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
		self.processLine(self.con.read_until("\n"))

if __name__ == '__main__':
	print "Starting up..."
	
	con = TelnetConnector()
	db = DB()

	while True:
		try:
			proc.Parser()
			time.sleep(0.5)
		except: raise