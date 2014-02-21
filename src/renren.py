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

from logger import debug, info, warn, error, fatal, stackTrace
import requests
import re
import random
import os
import sys
from encrypt import encryptString
import getpass
import urllib

# Encoding fix.

reload(sys)
sys.setdefaultencoding('UTF-8')

class RenRen:

	def __init__(self):
		self.session = requests.Session()
		self.session.headers.update({
			'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1833.5 Safari/537.36"
		})
		self.has_login = False
		self.token = {}

	def login(self, mail, passwd):
		key = self.getEncryptKey()
		debug('EncryptKey=' + str(key))

		if self.requireCaptcha(mail):
			warn('Captcha is required for account ' + mail)
			fn = 'icode.%s.jpg' % os.getpid()
			self.getICode(fn)
			info("Please open file '%s' and input the code" % fn)
			icode = raw_input().strip()
			os.remove(fn)
		else:
			icode = ''

		data = {
			'email': mail,
			'origURL': 'http://www.renren.com/home',
			'icode': icode,
			'domain': 'renren.com',
			'key_id': 1,
			'captcha_type': 'web_login',
			'password': self.encryptPassword(passwd, key),
			'rkey': key.get('rkey')
		}
		debug('Post Data: %s' % urllib.urlencode(data))
		url = 'http://www.renren.com/ajaxLogin/login?1=1&uniqueTimestamp=%f' % random.random()
		r = self.post(url, data)
		result = r.json()
		if result['code']:
			info('Successfully logged in as ' + mail)
			self.email = mail
		else:
			error('Login Failed!')
			error('Reason: ' + str(type(result['failDescription'])))
			raise RuntimeError()

	def encryptPassword(self, passwd, key):
		debug('Encryption: ' + ('enabled' if key['isEncrypted'] else 'disabled'))
		if not key['isEncrypted']:
			return passwd
		encrypted = encryptString(key['e'], key['n'], passwd)
		info('Encrypted password: ' + encrypted)
		return encrypted

	def getICode(self, fn):
		try:
			r = self.get("http://icode.renren.com/getcode.do?t=web_login&rnd=%s" % random.random())
		except requests.RequestException:
			error('Unable to get captcha! (Network problem?)')
			return
		if r.status_code == 200 and r.raw.headers['content-type'].lower() == 'image/jpeg':
			with open(fn, 'wb') as f:
				for chunk in r.iter_content():
					f.write(chunk)
		else:
			error('Unable to get captcha! (Not an image?)')

	def requireCaptcha(self, mail=None):
		res = self.post('http://www.renren.com/ajax/ShowCaptcha', data={'email': mail})
		try:
			res = int(res)
		except:
			pass
		return res
		# return r.json()

	def getEncryptKey(self):
		r = requests.get('http://login.renren.com/ajax/getEncryptKey')

		return r.json()

	def getToken(self):
		p = re.compile("get_check:'(.*)',get_check_x:'(.*)',env")

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

