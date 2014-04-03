
# Taken from skybot (https://github.com/rmmh/skybot/)

from plugin import Plugin

class Bitcoin(Plugin):
	def __init__(self, dong, conf):
		super(Bitcoin, self).__init__(dong, conf)
		
	def bitcoin(self, callback, who, loc):
		"""Gets the current exchange rate for bitcoins from mtgox."""
		
		data = self.get_json("https://btc-e.com/api/2/btc_usd/ticker")
		ticker = data['ticker']
		return "Current: $%(buy).2f - High: $%(high).2f" \
			" - Low: $%(low).2f - Volume: %(vol)s" % ticker
