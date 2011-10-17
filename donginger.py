#!/usr/bin/python

import os
import re
import sys
import json
import time
import telnetlib
import sqlite3 as sqlite

sys.path += ['plugins']

CONFIG = 'donginger.conf'

class Dong(object):
	pass

def parse_conf():
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
		self.tn = telnetlib.Telnet(dong.config['host'], dong.config['port'])
		self.read_until(" connected)")
		self.write("connect %s %s" % (dong.config['username'], dong.config['password']))
		if dong.config['first_command']:
			self.write(dong.config['first_command'])
		print 'Connected.'

	def write(self, str):
		if self.tn:
			self.tn.write(str + '\n')
		else:
			print 'No running telnet connection.'
			sys.exit(1)
			
	def read_until(self, str):
		if self.tn:
			return self.tn.read_until(str)
		else:
			print 'No running telnet connection.'
			sys.exit(1)


class Processor:
	def __init__(self):
		self.ansi_pat = re.compile('\033\[[0-9;]+m')
		self.chat_pat = re.compile('(.+?) (says|asks|exclaims), \"(.+)\"')
		
	def strip_ansi(self, str):
		return self.ansi_pat.sub('', str)
	
	def parser(self):
		buf = con.read_until('\n')
		buf = self.strip_ansi(buf)
		line = buf.split(' ', 4)
		
		# This makes sure Donginger does not catch what he says
		if line[0] == dong.config['bot_objnum'] and line[1] != dong.config['bot_objnum']:
			
			# Network broadcasts
			if line[3] in dong.config['monitored_nets']:
				self.process_network(self, line)

	def dispatch(self, plugin, callback, args):
		dong.plugins[plugin](callback)(args)
		
	def process_network(self, line):
		ntalk = re.search(self.chat_pat, line[4])
		author = ntalk.group(1)
		text = ntalk.group(3)
		
		cmd = text.split()
		if cmd in dong.commands.keys():
			self.dispatch(dong.commands[cmd[0]][0], dong.commands[cmd[0]][1], cmd[1:])


if __name__ == '__main__':
	print "Starting up..."
	
	dong = Dong()
	parse_conf()
	dong.db = DB()
	con = TelnetConnector()
	con.connect()
	proc = Processor()

	while True:
		try:
			proc.parser()
			time.sleep(0.5)
		except: raise