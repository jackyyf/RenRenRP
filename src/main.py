from renren import RenRen

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
			if not renren.console_login():
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
					current = time.gmtime()
					if current.tm_hour == 15 and current.tm_min >= 30: # Since China is GMT +0800
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
		print 'Received SIGINT, exiting...'
