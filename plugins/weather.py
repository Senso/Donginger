import urllib2
from lxml import etree
from urllib import urlencode


class Weather:
	def __init__(self, name, dong):
		self.name = name
		self.dong = dong
		self.conf = self.dong.plugins_conf[name]
		
	def build_query(self, url, params):
		query_string = urlencode(params)
		request = urllib2.Request(url + '?' + query_string)
		opener = urllib2.build_opener()
		return opener.open(request)
		
	def fetch_weather(self, who, loc):
		
		# Fetch cached location if not provided
		if not loc:
			self.dong.db.session.query(self.dong.db.tables['weather']).where(('user', who))
		else:
			self.dong.db.insert('weather', {'user': who, 'location': loc})
			
		w = self.build_query('http://www.google.com/ig/api', {'weather': loc})
		
		xml = etree.fromstring(w.read())
		
		return self.process_xml(xml)
		
	def process_xml(self, xml):
		if xml is None:
			return None
		
		xml = xml.find('weather')
		
		info = dict((e.tag, e.get('data')) for e in xml.find('current_conditions'))
		info['city'] = xml.find('forecast_information/city').get('data')
		info['high'] = xml.find('forecast_conditions/high').get('data')
		info['low'] = xml.find('forecast_conditions/low').get('data')
		
		try:
			return '%(city)s: %(condition)s, %(temp_f)sF/%(temp_c)sC (H:%(high)sF'\
					', L:%(low)sF), %(humidity)s, %(wind_condition)s.' % info
		except:
			pass
		
		
		
		