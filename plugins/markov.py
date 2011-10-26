
import re
import random
from time import time
from heapq import merge

from plugin import Plugin

class Markov(Plugin):
	""" Markov Chain plugin, inspired by the example here:
		http://www.evanfosmark.com/2009/11/python-markov-chains-and-how-to-use-them/
		Simplified for my case, did not need defaultdicts and I wanted more randomization.
	"""

	class START(object):pass
	class END(object):pass

	def __init__(self, dong, conf):
		super(Markov, self).__init__(dong, conf)

		self.wordpat = re.compile('.*?([a-zA-Z0-9\'\-]+).*?')
		self.texts = self.conf['texts'] 
		self.chains = {}
		self.process_all_texts()
		
	def markov_request(self, line, who, arg):
		"""Depending on the command, returns a Markov Chain from a specific text."""
		
		for chain in self.chains.keys():
			if line.find(chain) > -1:
				blurb = self.random_output(chain)
				joined = ' '.join(blurb)
				if joined[-1:] not in ('.','!','?'):
					joined += '.'
				return joined

	def add(self, chain, iterable, tmp=False):
		"""	Since large texts can come in all sort of formats and be quite ugly to parse
			(ex. the Bible, with all its chapter numbers), I prefer using a pure "word"
			regexp instead of doing .split().
		"""
		
		item1 = item2 = self.START
		
		if tmp is True:
			chain = {}
		else:
			chain = self.chains[chain]
		
		for item3 in iterable:
			s = re.search(self.wordpat, item3)
			if s:
				item3 = s.group(1)

				chain.setdefault((item1, item2), []).append(item3)

				item1 = item2
				item2 = item3

		chain.setdefault((item1, item2), []).append(self.END)
		
		return chain
		
	def random_output(self, chain, words=12, tmp=False):
		output = []
		
		if tmp is not True:
			chain = self.chains[chain]

		# Randomize starting words
		item1, item2 = random.choice(chain.keys())

		max = random.randrange(words / 2, words * 2)
		for i in range(words):
			item3 = random.choice(chain[(item1, item2)])
			if item3 is self.END:
				break

			item1 = item2
			item2 = item3

			output.append(item3)
		return output
	
	def process_all_texts(self):
		for name,file in self.texts.items():
			now = time()
			self.add_body(name, file)
			then = time()
			print "Processed %s (%s items) in %s seconds." % (name, len(self.chains[name]), round((then - now), 3))

	def add_body(self, name, file):
		self.chains[name] = {}
		full = open(file).read()
		words = full.split(' ')
		self.add(name, words)
		
	def markov_chat(self, line, who, arg):
		"""Returns a markov chain from one of the chat archives."""
		
		if arg in self.dong.config['archival']:
			rows = self.dong.db.select_all(arg)
			full_txt = []
			for row in rows:
				full_txt.append(row[1].split(' '))

			chain = self.add(None, list(merge(*full_txt)), True)
			output = self.random_output(chain, tmp=True)
			return ' '.join(output)
				
			
			
