
import json
import urllib2
from lxml import etree, html
from urllib import urlencode

class Plugin(object):
	
	def __init__(self, name, dong):
		self.name = name
		self.dong = dong
		self.conf = self.dong.plugins_conf[name]
		
	def build_query(self, url, params=None):
		if params:
			query_string = urlencode(params)
			request = urllib2.Request(url + '?' + query_string)
		else:
			request = urllib2.Request(url)
		opener = urllib2.build_opener()
		return opener.open(request)
		
	def get_html(self, url, params=None):
		return html.fromstring(self.build_query(url, params).read())
	
	def get_json(self, url, params=None):
		return json.loads(self.build_query(url, params).read())
		
	def get_xml(self, url, params=None):
		return (etree.fromstring(self.build_query(url, params).read()))
		