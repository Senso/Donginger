
import json
import urllib2
from lxml import etree, html
from urllib import urlencode

class Plugin(object):
	
	def __init__(self, dong, conf):
		self.dong = dong
		self.conf = conf
		
	def build_query(self, url, params=None, get_method=None):

		if params:
			query_string = urlencode(params)
			if url.find('?') > -1:	
				request = urllib2.Request(url + '&' + query_string)
			else:
				request = urllib2.Request(url + '?' + query_string)
		else:
			request = urllib2.Request(url)

		if get_method is not None:
			request.get_method = lambda: get_method

		opener = urllib2.build_opener()
		return opener.open(request)

	def get_head(self, url):
		return self.build_query(url, get_method='HEAD').read()

	def get_html(self, url, params=None, get_method=None):
		return html.fromstring(self.build_query(url, params, get_method).read())
	
	def get_json(self, url, params=None):
		return json.loads(self.build_query(url, params).read())
		
	def get_xml(self, url, params=None):
		return (etree.fromstring(self.build_query(url, params).read()))
		
	def unescape(self, s):
		if not s.strip():
			return s
		return html.fromstring(s).text_content()
		
	def fromstring(self, str):
		return html.fromstring(str).text_content()
		
