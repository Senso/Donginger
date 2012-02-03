import json
from plugin import Plugin
from random import choice

class Google(Plugin):
	def __init__(self, dong, conf):
		super(Google, self).__init__(dong, conf)
		
	def google(self, callback, who, arg):
		"""<google string> - returns a random Google result."""
		
		parsed = self.api_get('web', arg)
		if not 200 <= parsed['responseStatus'] < 300:
			return
		if not parsed['responseData']['results']:
			return
		
		result = choice(parsed['responseData']['results'])

		title = self.unescape(result['titleNoFormatting'])
		content = self.unescape(result['content'])
		
		if len(content) == 0:
			content = "No description available"
		else:
			content = self.fromstring(content)
			
		out = '%s' % content
		out = ' '.join(out.split())
		out = out.strip('...')

		return out
		
	def api_get(self, kind, query):
		url = 'http://ajax.googleapis.com/ajax/services/search/%s?' \
			'v=1.0&safe=off'
		return self.get_json(url % kind, params={'q': query})