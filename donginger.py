#!/usr/bin/python

import os
import re
import sys
import json
import time
import glob
import telnetlib

# Local imports
import database

sys.path += ['plugins']

CONFIG = 'donginger.conf'

class Dong(object):
	pass

def parse_conf():
	"""Parses the main config file and all the plugins configs."""
	
	dong.commands = {}
	dong.plugins = {}
	dong.plugins_conf = {}
	
	# Load main config file
	try:
		dong.config = json.load(open(CONFIG))
		
	except ValueError, e:
		print "Error parsing configuration %s: " % CONFIG, e
		sys.exit(1)
		
	# Load individual plugins config
	config_set = set(glob.glob(os.path.join("plugins", "*.conf")))
	
	for filename in config_set:
		load_config(filename)
		
def load_plugins():
	for plugin in dong.plugins_conf.items():
		plug_entry = getattr(__import__(plugin[1]['file']),plugin[1]['file'].capitalize())
		dong.plugins[plugin[1]['plugin_name']] = plug_entry(plugin[0], dong)
		
		for call in plugin[1]['callbacks'].items():
			dong.commands[call[0]] = [plugin[0], call[1]]
			
		# Create the necessary tables for that plugin
		for table in dong.plugins_conf[plugin[0]]['db_tables'].items():
			dong.db.create_table(table)
		dong.db.metadata.create_all(dong.db.con)


def load_config(file):
	try:
		config_json = json.load(open(file))
		
	except ValueError, e:
		print "Error parsing plugin configuration %s:" % file, e
		sys.exit(1)
		
	dong.plugins_conf[config_json['plugin_name']] = config_json

class TelnetConnector:
	def __init__(self):
		self.tn = None
	
	def connect(self):
		self.tn = telnetlib.Telnet(dong.config['host'], dong.config['port'])
		self.read_until(" connected)")
		self.write("connect %s %s" % (dong.config['username'], dong.config['password']))
		if dong.config['first_command']:
			self.write(dong.config['first_command'])

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
		buf = buf.strip('\r\n')
		buf = self.strip_ansi(buf)
		line = buf.split(' ', 4)
		
		# This makes sure Donginger does not catch what he says
		if line[0] == dong.config['bot_objnum'] and line[1] != dong.config['bot_objnum']:
			
			# Network broadcasts
			if line[3] in dong.config['monitored_nets']:
				self.process_network(line)
			
			# Direct talk
			# TODO: This needs to be configurable
			elif line[2] in ('-donginger', '-dong'):
				self.process_talk(line)
			

	def dispatch(self, plugin, callback, args):
		func = getattr(dong.plugins[plugin], callback, None)
		if func:
			func(args)
		
	def process_network(self, line):
		ntalk = re.search(self.chat_pat, line[4])
		if ntalk:
			author = ntalk.group(1)
			text = ntalk.group(3)
		
			cmd = text.split()
			if cmd[0] in dong.commands.keys():
				self.dispatch(dong.commands[cmd[0]][0], dong.commands[cmd[0]][1], ' '.join(cmd[1:]))
			
	def process_talk(self, line):
		cmd = line[3]
		if len(line) == 5:
			args = line[4]
		else:
			args = None
		
		if cmd in dong.commands.keys():
			self.dispatch(dong.commands[cmd][0], dong.commands[cmd][1], args)


if __name__ == '__main__':
	print "Starting up..."
	
	dong = Dong()
		
	dong.db = database.Database()
	dong.db.create_engine()
	dong.db.test_connection()
	dong.db.create_session()
	
	parse_conf()
	load_plugins()
	
	con = TelnetConnector()
	con.connect()
	proc = Processor()
	
	print 'Started.'

	while True:
		try:
			proc.parser()
			time.sleep(0.5)
		except: raise
