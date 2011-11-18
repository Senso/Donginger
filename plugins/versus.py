# This plugin requires the Rand plugin to work.

from plugin import Plugin

class Versus(Plugin):
	def __init__(self, dong, conf):
		super(Versus, self).__init__(dong, conf)
		
	def versus(self, callback, who, arg):
		"""<player> vs <player> - returns random quotes from two players."""
		
		opps = re.search('(.+) vs (.+)', callback, re.I)
		if opps:
			rand = dong.plugins['rand']
			dude1 = rand.random_line(callback, who, opps.group(1))
			dude2 = rand.random_line(callback, who, opps.group(2))
			if dude1 and dude2:
				return (dude1, dude2)