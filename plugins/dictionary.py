from plugin import Plugin

class Dictionary(Plugin):
	def __init__(self, dong, conf):
		super(Dictionary, self).__init__(dong, conf)

	def urban(self, callback, who, arg):
		"""Search on urbandictionary.com"""

		url = 'http://www.urbandictionary.com/iphone/search/define'
		page = self.get_json(url, params={'term': arg})
		defs = page['list']

		if page['result_type'] == 'no_results':
			return 'not found.'
	
		out = defs[0]['word'] + ': ' + defs[0]['definition']
	
		if len(out) > 400:
			out = out[:out.rfind(' ', 0, 400)] + '...'
	
		return out
	
	def etymology(inp):
		"""Returns the etymology of the given word"""
	
		url = 'http://www.etymonline.com/index.php'
	
		h = self.get_html(url, params={'term': arg})
	
		etym = h.xpath('//dl')
	
		if not etym:
			return ''
	
		etym = etym[0].text_content()
	
		etym = ' '.join(etym.split())
	
		if len(etym) > 400:
			etym = etym[:etym.rfind(' ', 0, 400)] + ' ...'
	
		return etym