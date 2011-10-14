#!/usr/bin/python

import sys
import telnetlib
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
		
		return conf
	except:
		print 'Error parsing configuration.'
		sys.exit(1)
		
class Connector:
	def __init__(self):
		self.tn = None
	
	def connect(self):
		self.tn = telnetlib.Telnet(conf['host'], 7777)
		self.tn.read_until(" connected)")
		self.tn.write("connect %s %s\n" % (conf['username'], conf['password']))
		self.tn.write("@join dionysus\n")

	def write(self, str):
		if self.tn:
			self.tn.write(str + '\n')
		else:
			print 'No running telnet connection.'

if __name__ == '__main__':
	print "Starting up..."
	
	con = Connector()
	proc = Processor(con)
	twit = Twit()

	while True:
		try:
			proc.Parser()
			time.sleep(0.5)
		except: raise