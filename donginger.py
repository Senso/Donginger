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
	"""Load an instance of each plugin class and create the DB tables if needed."""
	
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
	"""All the text parsing and command matching happens here."""
	
	def __init__(self):
		self.ansi_pat = re.compile('\033\[[0-9;]+m')
		self.chat_pat = re.compile("\[(%s)\] (.+?) (says|asks|exclaims), \"(.+)\"" % '|'.join(dong.config['monitored_nets']))
		
		# Line format is specific to each game/server and this will have to be adapted.
		# In the case of HellMOO, the format is as follow:
		# bot_objnum caller_name (caller_objnum) verb argstr
		self.line_pat = re.compile('(\#[0-9]+) (.+) \((\#[0-9]+)\) (.+?) (.+)')
		
	def strip_ansi(self, str):
		return self.ansi_pat.sub('', str)
	
	def parser(self):
		"""Matches a single line, determine if someone is talking to the bot."""
		
		buf = con.read_until('\n')
		buf = buf.strip('\r\n')
		buf = self.strip_ansi(buf)
		
		buf_match = re.search(self.line_pat, buf)
		if buf_match:
			caller_name = buf_match.group(2)
			caller_obj  = buf_match.group(3)
			verb        = buf_match.group(4)
			line        = buf_match.group(5)
		else:
			return
		
		# Avoid parsing anything done by the bot to prevent loops.
		if caller_name == dong.config['username']:
			return
		
		# Direct talk or paging shortcut
		elif verb[0] in ('`', '-', '\'') and verb[1:].lower() in dong.config['aliases']:
			self.process_line(caller_name, line, caller_name)
			
		# Proper paging using the 'page' command
		# Quite an ugly hack
		elif verb == 'page':
			prefix = [alias for alias in dong.config['aliases'] if line.startswith(alias)]
			for p in prefix:
				line = re.sub("^%s " % p, '', line)
			self.process_line(caller_name, line, caller_name)
		
		# net (channel) talk	
		net_match = re.search(self.chat_pat, line)
		if net_match:
			self.process_line(caller_name, net_match.group(4), net_match.group(1))

	def dispatch(self, plugin, callback, argstr):
		"""Call the actual method on the plugin."""
		
		func = getattr(dong.plugins[plugin], callback, None)
		if func:
			return func(argstr.strip())
			
	def process_line(self, caller, line, channel=None):
		"""Find if a command is triggered and do post-callback processing."""
		
		cmd = self.match_command(line)
		if cmd:
			# This removes the command from the line of text itself, leaving on the rest
			argstr = line[len(cmd):]
			response = self.dispatch(dong.commands[cmd][0], dong.commands[cmd][1], argstr)
			
			if response:
				# TODO: add proper response handling
				if channel:
					con.write('dong ' + response)
				pass

		if channel:
			# TODO: network chat archival here
			pass
			
	def match_command(self, line):
		commands = dong.commands.keys()
		command = [cmd for cmd in commands if line.startswith(cmd)]
		
		if len(command) == 1:
			return command[0]

		return None


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
			time.sleep(0.3)
		except: raise
