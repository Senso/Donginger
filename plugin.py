
class Plugin(object):
	def __init__(self, name, dong):
		self.name = name
		self.dong = dong
		self.conf = self.dong.plugins_conf[name]