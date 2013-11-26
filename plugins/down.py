from plugin import Plugin
import urlparse

class Down(Plugin):
	def __init__(self, dong, conf):
		super(Down, self).__init__(dong, conf)

	def down(self, callback, who, arg):
		"""down <url> -- checks to see if the site is down."""

		if 'http://' not in arg:
			inp = 'http://' + arg
		inp = 'http://' + urlparse.urlparse(inp).netloc

		try:
			p = Plugin('wow', 'such doge')
			p.get_head(url=inp)
			return inp + ' seems to be up.'
		except:
			return inp + ' seems to be down.'
