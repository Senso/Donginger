
class Plugin(object):
	
	def __init__(self, name, dong):
		self.name = name
		self.dong = dong
		self.conf = self.dong.plugins_conf[name]
		
	def build_query(self, url, params):
		query_string = urlencode(params)
		request = urllib2.Request(url + '?' + query_string)
		opener = urllib2.build_opener()
		return opener.open(request)