#!/usr/bin/python

import os
import re
import sys
import json
import time
import glob
import telnetlib
from datetime import datetime

# Local imports
import database

sys.path += ['plugins']

CONFIG = 'conf/donginger.conf'

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
	
	# Create the tables needed for chat archival
	if dong.config['archival']:
		for net in dong.config['archival']:
			table_schema = [net, {"time": "datetime",
									"author": "string",
									"message": "string"
								}
							]
			dong.db.create_table(table_schema)
		
	# Importing the .py plugins then loading its config, if it exists.
	plugin_set = set(glob.glob(os.path.join("plugins", "*.py")))
	for filename in plugin_set:
		load_plugin(filename)
		
def load_plugin(filename):
	module = re.sub('plugins/', '', filename)
	module = re.sub('\.py', '', module)
	
	if os.path.exists("conf/%s.conf" % module):
		plug_conf = load_config("conf/%s.conf" % module)
	else:
		# Build a dummy minimal config set
		plug_conf = {"callbacks": {module: module}}
		
	for call in plug_conf['callbacks'].items():
		dong.commands[call[0]] = [module, call[1]]
	
	plug_entry = getattr(__import__(module), module.capitalize())
	dong.plugins[module] = plug_entry(dong, plug_conf)
	
	try:
		tbl_info = plug_conf['db_tables']
	except:
		# No tables defined
		return
		
	# Create the necessary tables for that plugin
	for table in tbl_info.items():
		dong.db.create_table(table)
	dong.db.metadata.create_all(dong.db.con)

def load_config(file):
	try:
		config_json = json.load(open(file))
		
	except ValueError, e:
		print "Error parsing plugin configuration %s:" % file, e
		sys.exit(1)
	
	return config_json

class TelnetConnector:
	def __init__(self):
		self.tn = None
	
	def connect(self):
		self.tn = telnetlib.Telnet(dong.config['host'], dong.config['port'])
		self.read_until(" connected)")
		self.write("connect %s %s" % (dong.config['username'], dong.config['password']))
		if dong.config['first_commands']:
			for cmd in dong.config['first_commands']:
				self.write(cmd)

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
		self.chat_pat = re.compile("\[(%s)\] (.+?) (says|asks|exclaims), \"(.+)\"" % '|'.join(dong.config['monitored_nets'].keys()))
		
		# Line format is specific to each game/server and this will have to be adapted.
		# In the case of HellMOO, the format is as follow:
		# bot_objnum caller_name (caller_objnum) verb argstr
		self.line_pat = re.compile('(\#[0-9]+) (.+) \((\#[0-9]+)\) (.+?) (.+)', re.I)
		
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
			if verb[0] == '\'':
				verb = 'page'
			self.process_line(caller_name, line, caller_name)
			
		# Proper paging using the 'page' command
		# Quite an ugly hack
		elif verb == 'page':
			# This bit remove Donginger's name from the actual text
			prefix = [alias for alias in dong.config['aliases'] if line.startswith(alias)]
			for p in prefix:
				line = re.sub("^%s " % p, '', line)
	
			self.process_line(caller_name, line, caller_name, page=True)

		# This is for direct verb commands (ex. 'nudge')
		elif verb in dong.commands:
			self.process_line(caller_name, verb + ' ' + line, caller_name)
		
		# net (channel) talk	
		net_match = re.search(self.chat_pat, line)
		if net_match:
			self.process_line(caller_name, net_match.group(4), net_match.group(1))

	def dispatch(self, plugin, callback, line, caller, argstr):
		"""Call the actual method on the plugin."""
		
		func = getattr(dong.plugins[plugin], callback, None)
		if func:
			return func(line, caller, argstr.strip())
			
	def archive_line(self, channel, caller, line):
		dong.db.insert(channel, {'time': datetime.now(), 'author': caller, 'message': line})
			
	def process_line(self, caller, line, source, page=False):
		"""Find if a command is triggered and do post-dispatch processing."""
		
		def spew(resp):
			if page:
				con.write("page %s %s" % (caller, resp))
			elif source in dong.config['monitored_nets'].keys() and dong.config['monitored_nets'][source] == 'read-write':
				con.write("%s %s" % (source[:-3], resp))
			else:
				con.write("-%s %s" % (caller, resp))

		cmd = self.match_command(line)
		if cmd:
			# This removes the command from the line of text itself, leaving on the rest
			argstr = line[len(cmd):]
			response = self.dispatch(dong.commands[cmd][0], dong.commands[cmd][1], line, caller, argstr)
			
			if type(response) == tuple:
				for r_line in response:
					spew(r_line)
			elif response:
				spew(response)

		# Let's not archive commands themselves, that would be dumb
		if not cmd:
			if source and source in dong.config['archival']:
				self.archive_line(source, caller, line)
			
	def match_command(self, line):
		for cmd in dong.commands.keys():
			# wildcards in commands
			if cmd.find('<%>') > -1:
				cmd_match = re.search(cmd.replace('<%>', '(.+)'), line)
				if cmd_match:
					return cmd

			# Priority to commands matching the exact name
			elif line.split()[0] == cmd:
				return cmd
			
			# Standard: line starts with the command
			elif line.startswith(cmd):
				return cmd
			
		return None


if __name__ == '__main__':
	print "Starting up..."
	
	dong = Dong()
		
	dong.db = database.Database()
	dong.db.create_engine()
	dong.db.test_connection()
	dong.db.create_session()
	
	parse_conf()
	
	con = TelnetConnector()
	con.connect()
	proc = Processor()
	
	print 'Started.'

	while True:
		try:
			proc.parser()
			time.sleep(0.3)
		except Exception, e:
			print e
