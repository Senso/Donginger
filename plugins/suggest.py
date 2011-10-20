
import json
from plugin import Plugin
from random import choice

class Suggest(Plugin):
	def __init__(self, name, dong):
		super(Suggest, self).__init__(name, dong)
		
	def google_suggest(self, who, str):
		w = self.build_query('http://google.com/complete/search', {'q': str})
		page = w.read()
		page_json = page.split('(', 1)[1][:-1]
		suggestions = json.loads(page_json)[1][0]
		if suggestions:
			suggestions = self.remove_lyrics(suggestions)
			random_sug = choice(suggestions)
			self.store_suggestion(who, str)
			return random_sug
			
	def remove_lyrics(self, sug):
		nyt = []
		for s in sug:
			if s.find('lyrics') > -1: pass
			else: nyt.append(s)
		return nyt
	
	def store_suggestion(self, who, sug):
		sug = sug.strip('\r')
		sug = sug.strip()
		
		try:
			self.dong.db.insert('suggest', {'user': who, 'suggestion': sug})
		except:
			# UNIQUE constraint will balk here
			pass
		
	def pull_suggestion(self, *args):
		random_sug = self.dong.db.get_random_row('suggest')
		res = self.google_suggest(random_sug)
		return res

	
