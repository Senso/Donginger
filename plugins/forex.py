
# Taken from skybot (https://github.com/rmmh/skybot/)

from plugin import Plugin

class Forex(Plugin):
	def __init__(self, dong, conf):
		super(Forex, self).__init__(dong, conf)
		
	def forex(self, callback, who, curs):
		"""Gets the current exchange rate for virtual currencies from vircurex.com."""
		
		first, second = curs.split(" ")

		data = self.get_json_https("https://vircurex.com/api/get_highest_bid.json?base=%s&alt=%s" % (first.upper(), second.upper()))
		#print 'data', data
		return "%s to %s exchange rate: %s" % (first.upper(), second.upper(), data['value'])
