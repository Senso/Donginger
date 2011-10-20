
from plugin import Plugin

class Help(Plugin):
	def __init__(self, name, dong):
		super(Help, self).__init__(name, dong)
		
	def help(self, who, cmd):
		if cmd:
			try:
				plugin, cb = self.dong.commands[cmd]
				func = getattr(dong.plugins[plugin], cb)
				doc = func.__doc__
				if doc:
					return "Help for %s: %s" % (cmd, doc)
				else:
					return "No help for %s" % cmd
			except:
				return "Command not found: %s" % cmd
		else:
			cmd_list = ', '.join(self.dong.commands.keys())
			return "Available commands: %s" % cmd_list
		