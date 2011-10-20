
from plugin import Plugin
from lxml import etree

class Weather(Plugin):
	def __init__(self, name, dong):
		super(Weather, self).__init__(name, dong)
		
	def fetch_weather(self, who, loc):
		"""<weather location> returns the weather for that location. Not providing a location makes it returns the weather of your last used location."""
		
		# Check if we already have that user in the DB
		table = self.dong.db.tables['weather']
		q = self.dong.db.session.query(table).filter(getattr(table.c, 'user') == who)
		
		# Fetch cached location if not provided
		if not loc:
			try:
				loc = q.all()[0][1]
			except:
				loc = ''
		else:
			db_loc = q.all()
			if db_loc:
				self.dong.db.update('weather', {'user': who}, {'location': loc})
			else:
				self.dong.db.insert('weather', {'user': who, 'location': loc})
			
		w = self.build_query('http://www.google.com/ig/api', {'weather': loc})
		
		xml = etree.fromstring(w.read())
		
		return self.process_xml(xml)
		
	def process_xml(self, xml):
		if xml is None:
			return None
		
		xml = xml.find('weather')
		
		if xml.find('problem_cause') is not None:
			return None
		
		info = dict((e.tag, e.get('data')) for e in xml.find('current_conditions'))
		info['city'] = xml.find('forecast_information/city').get('data')
		info['high'] = xml.find('forecast_conditions/high').get('data')
		info['low'] = xml.find('forecast_conditions/low').get('data')
		
		try:
			return '%(city)s: %(condition)s, %(temp_f)sF/%(temp_c)sC (H:%(high)sF'\
					', L:%(low)sF), %(humidity)s, %(wind_condition)s.' % info
		except:
			pass
		
		
		
		