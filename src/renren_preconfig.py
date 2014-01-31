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

# Account Information

RenRenEmail	= 'yourname@example.com'
RenRenPass	= 'your.password_here'

import requests
import re
import os
import random
import time
from encrypt import encryptString
import sys
import getpass
import traceback

class RenRen:

	def __init__(self, email=None, pwd=None):
		self.session = requests.Session()
		self.token = {}

		if email and pwd:
			self.login(email, pwd)

	def login(self, email, pwd):
		key = self.getEncryptKey()
		print key

		if self.getShowCaptcha(email) == 1:
			fn = 'icode.%s.jpg' % os.getpid()
			self.getICode(fn)
			print "Please input the code in file '%s':" % fn
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
			'rkey': key.get('rkey', '')
		}
		print "login data: %s" % data
		url = 'http://www.renren.com/ajaxLogin/login?1=1&uniqueTimestamp=%f' % random.random()
		r = self.post(url, data)
		result = r.json()
		if result['code']:
			print 'Login OK'
			self.email = email
			r = self.get(result['homeUrl'])
			self.getToken(r.text)
		else:
			print 'Login Failed!'
			print r.text
			raise RuntimeError()

	def getICode(self, fn):
		r = self.get("http://icode.renren.com/getcode.do?t=web_login&rnd=%s" % random.random())
		if r.status_code == 200 and r.raw.headers['content-type'] == 'image/jpeg':
			with open(fn, 'wb') as f:
				for chunk in r.iter_content():
					f.write(chunk)
		else:
			print "get icode failure"

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

	def _login(self):
		try:
			self.login(RenRenEmail, RenRenPass)
		except RuntimeError:
			return False
		return True

RPIntervalBefore	= '<input type="hidden" id="interval" value=\''
RPIntervalAfter		= '\'/>'
RPAmountBefore		= '<input type="hidden" id="refreshRp" value=\''
RPAmountAfter		= '\'/>'

if __name__ == '__main__':

	print 'If you have any problem, please open an issue at https://github.com/jackyyf/RenRenRP'

	# print 'RenRen Refresh Daemon, PID = %d' % os.getpid()

	renren = RenRen()

	try:
		while True:
			if not renren._login():
				continue
			while True:
				try:
					content = renren.RPRefresh()
				except KeyboardInterrupt:
					raise
				except:
					traceback.print_exc()
					print 'Error! Login Again...'
					break
				pos = content.find(RPIntervalBefore)
				if pos == -1:
					print 'No RP Info... Need to login again?'
					print 'If your account and password is right, but still get this error message again and again,'
					print 'please open an issue at https://github.com/jackyyf/RenRenRP'
					break
				else:
					epos = content.find(RPIntervalAfter, pos)
					if epos == -1:
						print 'Please open an issue at https://github.com/jackyyf/RenRenRP, sorry for inconvenience.'
						sys.exit(1)
					interval = max(int(content[pos + len(RPIntervalBefore) : epos]) / 1000.0, 0.0)
					# Interval fix: maybe a new day is coming?
					# Using time.localtime, Please set timezone to GMT +0800
					current = time.localtime()
					if current.tm_hour == 23 and current.tm_min >= 30:
						secLeft = float(3600 - current.tm_min * 60 - current.tm_sec)
						interval = min(secLeft, interval)
					print 'Time left to get another RP Point: %.3f seconds' % interval
					p1 = content.find(RPAmountBefore)
					if p1 == -1:
						print 'Refresh RP amount not found (format changed?). Ignored.'
					else:
						p2 = content.find(RPAmountAfter, p1)
						if p2 == -1:
							print 'Refresh RP amount not found (format changed?). Ignored.'
						else:
							print 'Today RP amount earned by refreshing = %s' % content[p1 + len(RPAmountBefore) : p2]
					realSleep = min(max(interval - 1.0, 0.0), 300.0)
					print 'Sleep %.3f seconds before another refresh ...' % realSleep
					time.sleep(realSleep)
	except KeyboardInterrupt:
		print 'SIGINT received, exiting...'
