
from random import choice
from plugin import Plugin

class Rand(Plugin):
	def __init__(self, dong, conf):
		super(Rand, self).__init__(dong, conf)
		
	def random_line(self, callback, who, arg):
		all_lines = []
		for net in self.dong.config['archival']:
			rows = self.dong.db.select_where(net, ('author', arg), field='message')
			for row in rows:
				all_lines.append(row[0])
				
		if all_lines:
			one = choice(all_lines)
			return "<%s> %s" % (arg, one)