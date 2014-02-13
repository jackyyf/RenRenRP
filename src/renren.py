#!/usr/bin/python
#-*-coding:utf-8-*-

"""
Copyright (c) 2012 wong2 <wonderfuly@gmail.com>
Copyright (c) 2012 hupili <hpl1989@gmail.com>
Copyright (c) 2014 jackyyf <root@jackyyf.com>

Original Author:
	Wong2 <wonderfuly@gmail.com>
Changes Statement:
	Changes made by Pili Hu <hpl1989@gmail.com> on
	Jan 10 2013:
		Support captcha.
	Changes made by Yifu Yu <root@jackyyf.com> on
	Jan 24 2014:
		Add RenRenRP refresh support, remove unused function.

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
'Software'), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

__version__	= '0.1.0a'
__author__	= 'jackyyf <root@jackyyf.com>'

import logger
import requests
import re
import random
import time
import os
from encrypt import encryptString
import sys
import getpass
import traceback
import urllib

class RenRen:

	def __init__(self, email=None, pwd=None):
		self.session = requests.Session()
		self.has_login = False
		self.token = {}

		if email and pwd:
			self.login(email, pwd)

	def login(self, email, pwd):
		key = self.getEncryptKey()
		logger.debug('EncryptKey=' + str(key))

		if self.getShowCaptcha(email) == 1:
			logger.warn('Captcha is required for account ' + email)
			fn = 'icode.%s.jpg' % os.getpid()
			self.getICode(fn)
			logger.info("Please open file '%s' and input the code" % fn)
			icode = raw_input().strip()
			os.remove(fn)
		else:
			icode = ''

		data = {
			'email': email,
			'origURL': 'http://www.renren.com/home',
			'icode': icode,
			'domain': 'renren.com',
			'key_id': 1,
			'captcha_type': 'web_login',
			'password': encryptString(key['e'], key['n'], pwd) if key['isEncrypt'] else pwd,
			'rkey': key.get('rkey')
		}
		logger.debug('Post Data: %s' % urllib.urlencode(data))
		url = 'http://www.renren.com/ajaxLogin/login?1=1&uniqueTimestamp=%f' % random.random()
		r = self.post(url, data)
		result = r.json()
		if result['code']:
			logger.info('Successfully logged in as ' + email)
			self.email = email
			r = self.get(result['homeUrl'])
			self.getToken(r.text)
		else:
			logger.error('Login Faied!')
			logger.error('Reason: ' + str(type(result['failDescription'])))
			raise RuntimeError()

	def getICode(self, fn):
		r = self.get("http://icode.renren.com/getcode.do?t=web_login&rnd=%s" % random.random())
		if r.status_code == 200 and r.raw.headers['content-type'] == 'image/jpeg':
			with open(fn, 'wb') as f:
				for chunk in r.iter_content():
					f.write(chunk)
		else:
			logger.error('Unable to get captcha! (Network issue?)')

	def getShowCaptcha(self, email=None):
		r = self.post('http://www.renren.com/ajax/ShowCaptcha', data={'email': email})
		return r.json()

	def getEncryptKey(self):
		r = requests.get('http://login.renren.com/ajax/getEncryptKey')
		return r.json()

	def getToken(self, html=''):
		p = re.compile("get_check:'(.*)',get_check_x:'(.*)',env")

		if not html:
			r = self.get('http://www.renren.com')
			html = r.text

		result = p.search(html)
		self.token = {
			'requestToken': result.group(1),
			'_rtk': result.group(2)
		}

	def request(self, url, method, data={}):
		if data:
			data.update(self.token)

		self.session.headers.update({
			'User-Agent'	:	"Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1797.2 Safari/537.36"
		})

		if method == 'get':
			return self.session.get(url, data=data)
		elif method == 'post':
			return self.session.post(url, data=data)

	def get(self, url, data={}):
		return self.request(url, 'get', data)

	def post(self, url, data={}):
		return self.request(url, 'post', data)

	def RPRefresh(self):
		return self.get('http://www.renren.com/home').content # Use a 302 redirect.

	def console_login(self):
		if not self.has_login:
			self._email = raw_input('Renren account (your email address): ')
			self._pwd	= getpass.getpass('Renren password (will not echoed):')
			self.has_login = True
		try:
			self.login(self._email, self._pwd)
		except RuntimeError:
			print 'Login Failed.'
			self.has_login = False
			return False
		return True

