#!/usr/bin/python

import os
import re
import sys
import json
import time
import glob
import telnetlib
from datetime import datetime
from optparse import OptionParser

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
	def __init__(self, debug):
		self.debug = debug
		self.tn = None
	
	def connect(self):
		self.tn = telnetlib.Telnet(dong.config['host'], dong.config['port'])
		self.read_until(" players)")
		self.write("connect %s %s" % (dong.config['username'], dong.config['password']))
		time.sleep(1)
		if dong.config['first_commands']:
			for cmd in dong.config['first_commands']:
				self.write(cmd)

	def write(self, str):
		if self.tn:
			#try:
			if self.debug:
				print '> ' + str
			self.tn.write(str + '\n')
			#except: pass
		else:
			print 'No running telnet connection.'
			sys.exit(1)
			
	def read_until(self, str):
		if self.tn:
			derp = self.tn.read_until(str)
			if self.debug:
				print derp
			return derp
		else:
			print 'No running telnet connection.'
			sys.exit(1)


class Processor:
	"""All the text parsing and command matching happens here."""
	
	def __init__(self):
		self.ansi_pat = re.compile('\033\[[0-9;]+m')
		#self.chat_pat = re.compile("\[(%s)\] \((.+?)\) (says|asks|exclaims), \"(.+)\"" % '|'.join(dong.config['monitored_nets'].keys()))
		self.chat_pat = re.compile("\[(%s)\] (.+) (says|asks|exclaims), \"(.+)\"" % '|'.join(dong.config['monitored_nets'].keys()))
		
		# Line format is specific to each game/server and this will have to be adapted.
		# In the case of HellMOO, the format is as follow:
		# bot_objnum caller_name (caller_objnum) verb argstr
		self.line_pat = re.compile('(\#[0-9]+) (.+) \((\#[0-9]+)\) (.+?) (.+)', re.I)
		self.private_caller = None
		self.private_msg = None
		
	def strip_ansi(self, str):
		return self.ansi_pat.sub('', str)
	
	def parser(self):
		"""Matches a single line, determine if someone is talking to the bot."""
		
		buf = con.read_until('\n')
		buf = buf.strip('\r\n')
		buf = self.strip_ansi(buf)

		## INTERRUPT EVERYTHING IF @PASTE-TO FOUND
		privpat = "\-+Private message from (.+?)\-\-"
		#privpat = "\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-Private message from (.+?)\-\-"
		privmatch = re.search(privpat, buf)
		if privmatch:
			self.private_caller = privmatch.group(1)
			self.private_msg = [buf]
			return
		if buf.find("--------------------------------end message") > -1:
#			print 'dialogue:', self.private_msg
			func = getattr(dong.plugins['pytoon'], 'main', None)
			if func:
#				print 'func called:', func
				ret = func(self.private_caller, self.private_msg)
#				self.private_caller = None
#				self.private_msg = None
#				print 'ret:', ret
#				return ret
				if ret:
					con.write("-%s %s" % (self.private_caller, ret))
				self.private_caller = None
				self.private_msg = None
			else:
				self.private_caller = None
				self.private_msg = None
		if self.private_msg is not None:
#			print 'appended:', buf
			self.private_msg.append(buf)
			return
		
		buf_match = re.search(self.line_pat, buf)
		if buf_match:
			caller_name = buf_match.group(2)
			caller_obj  = buf_match.group(3)
			verb        = buf_match.group(4)
			line        = buf_match.group(5)
		else:
			return
	
		# Avoid parsing anything done by the bot to prevent loops.
		if caller_name.lower() == dong.config['username'].lower():
			return
		if caller_obj == '#359878':
			return
        

		# Direct talk or paging shortcut
		elif verb[0] in ('`', '-', '\'') and verb[1:].lower() in dong.config['aliases']:
			if verb[0] == '\'':
				verb = 'page'
			else:
				self.process_line(caller_name, line, caller_name, obj=caller_obj)
				return
	
		# Proper paging using the 'page' command
		# Quite an ugly hack
		if verb == 'page':
			# This bit remove Donginger's name from the actual text
			prefix = [alias for alias in dong.config['aliases'] if line.startswith(alias)]
			for p in prefix:
				line = re.sub("^%s " % p, '', line)
	
			self.process_line(caller_name, line, caller_name, page=True, obj=caller_obj)

		# This is for direct verb commands (ex. 'nudge')
		elif verb in dong.commands:
			self.process_line(caller_name, verb + ' ' + line, caller_name, obj=caller_obj)

		elif verb == 'coinnet':
			net_match = re.search(self.chat_pat, line)
			self.process_line(caller_name, net_match.group(4), net_match.group(1), obj=caller_obj)
			return
	
		# net (channel) talk
		net_match = re.search(self.chat_pat, line)
		if net_match:
			self.process_line(caller_name, net_match.group(4), net_match.group(1), obj=caller_obj)

	def dispatch(self, plugin, callback, line, caller, argstr, obj):
		"""Call the actual method on the plugin."""
		
		func = getattr(dong.plugins[plugin], callback, None)
		if func:
			# HACK for special twitter perms
			if callback in ['post_tweet', 'riot_tweet',  
				'random_tweet', 'add_tag', 'del_tag', 'add_target', 'del_target']:
				return func(line, caller, argstr.strip(), obj)
			else:
				return func(line, caller, argstr.strip())
			
	def archive_line(self, channel, caller, line):
		dong.db.insert(channel, {'time': datetime.now(), 'author': caller, 'message': line})
			
	def process_line(self, caller, line, source, page=False, obj=None):
		"""Find if a command is triggered and do post-dispatch processing."""
		
		def spew(resp):
			if page:
				con.write("page %s %s" % (caller, resp))
			elif source in dong.config['monitored_nets'].keys() and dong.config['monitored_nets'][source] == 'read-write':
				con.write("%s %s" % (source[:-3], resp))
			else:
				con.write("-%s %s" % (caller, resp))

		if caller == 'Dionysus' and line.startswith('puppet:'):
			print 'puppet cmd:', line[7:]
			con.write("%s\n" % line[7:])
			return

		cmd = self.match_command(line)
		if cmd:
			# This removes the command from the line of text itself, leaving on the rest
			argstr = line[len(cmd):]
			response = self.dispatch(dong.commands[cmd][0], dong.commands[cmd][1], line, caller, argstr, obj)
			
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

			# Second pass at standard regex
			elif re.search(cmd, line):
				return cmd

			# Priority to commands matching the exact name
			elif line.split()[0].strip() == cmd:
				return cmd
			
			# Standard: line starts with the command
			elif line.strip().startswith(cmd):
				return cmd
			
		return None


if __name__ == '__main__':
	print "Starting up..."
	opts = OptionParser()
	opts.add_option('-d', '--debug', action='store_true', dest='debug', help='Enable stdout output', default=False)
	(options, args) = opts.parse_args()
	
	dong = Dong()
		
	dong.db = database.Database()
	dong.db.create_engine()
	dong.db.test_connection()
	dong.db.create_session()
	
	parse_conf()
	
	con = TelnetConnector(options.debug)
	con.connect()
	proc = Processor()
	
	print 'Started.'

	while True:
		try:
			proc.parser()
			time.sleep(0.3)
		except Exception, e:
			print e
