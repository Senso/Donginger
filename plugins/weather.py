import urllib2
from lxml import etree
from urllib import urlencode


class Weather:
	def __init__(self, name, dong):
		self.name = name
		self.dong = dong
		self.conf = self.dong.plugins_conf[name]
		
	def build_query(self, url, params):
		post_data = urlencode(params)
		request = urllib2.Request(url, post_data)
		opener = urllib2.build_opener()
		return opener.open(request)
		
	def fetch_weather(self, loc, who=None):
		
		# Fetch cached location if not provided
		if not loc:
			self.dong.db.session.query(self.dong.db.tables['weather']).where(('user', who))
			
		w = self.build_query('http://www.google.com/ig/api', {'weather': loc})
		
		xml = etree.fromstring(w.read())
		
		self.process_xml(xml)
		
	def process_xml(self, xml):
		if not xml:
			return None
		
		print xml