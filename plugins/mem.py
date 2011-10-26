
# Taken from skybot (https://github.com/rmmh/skybot/)

import os
import re

from plugin import Plugin

class Mem(Plugin):
	def __init__(self, dong, conf):
		super(Mem, self).__init__(dong, conf)
		
	def mem(self, callback, who, cmd):
		"""Returns the bot's current memory usage."""
		
		if os.name == 'posix':
			status_file = open("/proc/%d/status" % os.getpid()).read()
			line_pairs = re.findall(r"^(\w+):\s*(.*)\s*$", status_file, re.M)
			status = dict(line_pairs)
			keys = 'VmSize VmLib VmData VmExe VmRSS VmStk'.split()
			return ', '.join(key + ':' + status[key] for key in keys)
	
		elif os.name == 'nt':
			cmd = "tasklist /FI \"PID eq %s\" /FO CSV /NH" % os.getpid()
			out = os.popen(cmd).read()
	
			total = 0
			for amount in re.findall(r'([,0-9]+) K', out):
				total += int(amount.replace(',', ''))
	
			return 'memory usage: %d kB' % total