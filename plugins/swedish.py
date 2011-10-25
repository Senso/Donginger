
import re

from plugin import Plugin

class Swedish(Plugin):
	def __init__(self, name, dong):
		super(Swedish, self).__init__(name, dong)
		
	def swedish(self, callback, who, arg):
		subs = ((r'a([nu])', r'u\1'),
			(r'A([nu])', r'U\1'),
			(r'a\B', r'e'),
			(r'A\B', r'E'),
			(r'en\b', r'ee'),
			(r'\Bew', r'oo'),
			(r'\Be\b', r'e-a'),
			(r'\be', r'i'),
			(r'\bE', r'I'),
			(r'\Bf', r'ff'),
			(r'\Bir', r'ur'),
			(r'(\w*?)i(\w*?)$', r'\1ee\2'),
			(r'\bow', r'oo'),
			(r'\bo', r'oo'),
			(r'\bO', r'Oo'),
			(r'the', r'zee'),
			(r'The', r'Zee'),
			(r'th\b', r't'),
			(r'\Btion', r'shun'),
			(r'\Bu', r'oo'),
			(r'\BU', r'Oo'),
			(r'v', r'f'),
			(r'V', r'F'),
			(r'w', r'w'),
			(r'W', r'W'),
			(r'([a-z])[.]', r'\1.  Bork Bork Bork!'))
		
		line = arg
		for from_pat, to_pat in self.subs:
			line = re.sub(from_pat, to_pat, line)
		return line