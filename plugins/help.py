
from plugin import Plugin

class Help(Plugin):
	def __init__(self, dong, conf):
		super(Help, self).__init__(dong, conf)
		
	def help(self, callback, who, cmd):
		"""The help command."""
		
		if cmd:
			try:
				plugin, cb = self.dong.commands[cmd]
				func = getattr(self.dong.plugins[plugin], cb)
				doc = func.__doc__
				if doc:
					return "Help for %s: %s" % (cmd, doc)
				#else:
				#	return "No help for %s" % cmd
			except:
				pass
				#return "Command not found: %s" % cmd
		else:
			cmds = self.dong.commands.keys()
			clean_cmds = []
			for x in cmds:
				x = x.strip('$')
				x = x.strip('^')
				clean_cmds.append(x)
			cmd_list = ', '.join(clean_cmds)
			return "Available commands: %s" % cmd_list
		
