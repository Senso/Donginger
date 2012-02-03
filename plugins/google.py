import json
from plugin import Plugin
from random import choice

class Google(Plugin):
	def __init__(self, dong, conf):
		super(Google, self).__init__(dong, conf)
		
	def google(self, callback, who, arg):
		"""<google string> - returns a random Google result."""
		
		parsed = self.api_get('web', inp)
		if not 200 <= parsed['responseStatus'] < 300:
			return
		if not parsed['responseData']['results']:
			return
		
		result = parsed['responseData']['results'][0]

		title = self.unescape(result['titleNoFormatting'])
		content = self.unescape(result['content'])
		
		if len(content) == 0:
			content = "No description available"
		else:
			content = self.html.fromstring(content).text_content()
			
		out = '%s -- \x02%s\x02: "%s"' % (result['unescapedUrl'], title, content)
		out = ' '.join(out.split())

		if len(out) > 300:
			out = out[:out.rfind(' ')] + '..."'

		return out
		
	def api_get(self, kind, query):
		url = 'http://ajax.googleapis.com/ajax/services/search/%s?' \
			'v=1.0&safe=off'
		return self.get_json(url % kind, q=query)