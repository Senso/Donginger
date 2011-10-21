
# Taken from skybot (https://github.com/rmmh/skybot/)

from plugin import Plugin

class Bitcoin(Plugin):
	def __init__(self, name, dong):
		super(Bitcoin, self).__init__(name, dong)
		
	def bitcoin(self, callback, who, loc):
		"""Gets the current exchange rate for bitcoins from mtgox."""
		
		data = self.get_json("https://mtgox.com/code/data/ticker.php")
		ticker = data['ticker']
		return "Current: \x0307$%(buy).2f\x0f - High: \x0307$%(high).2f\x0f"
			" - Low: \x0307$%(low).2f\x0f - Volume: %(vol)s" % ticker