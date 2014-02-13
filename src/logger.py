#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import time
import traceback
from colorama import init as ConsoleInit, Fore, Back, Style, AnsiToWin32

class Level:
	DEBUG   = 0
	INFO	= 1
	WARN	= 2
	ERROR   = 3
	FATAL   = 4 # This log level will trigger a backtrace, and terminate thread with sys.exit(1)
	TRACE   = 5 # This is the level for backtrace only.

class _logger:

	_colors = {
		Level.DEBUG	: Fore.GREEN + Style.BRIGHT,
		Level.INFO	: Fore.BLUE + Style.BRIGHT,
		Level.WARN	: Fore.RED,
		Level.ERROR	: Fore.RED + Style.BRIGHT,
		Level.FATAL	: Fore.RED + Style.BRIGHT,
		Level.TRACE	: Fore.GREEN,
	}

	_levelStr = {
		Level.DEBUG	: 'DEBUG',
		Level.INFO	: 'INFO',
		Level.WARN	: 'WARN',
		Level.ERROR	: 'ERROR',
		Level.FATAL	: 'FATAL',
		Level.TRACE	: 'TRACE',
	}

	def __init__(self, f = None, colorize = True, level = None, log_format = None):
		'''
			log_format supports:
			time	-> Time in local timezone. (like what `date` outputs)
			clock	-> Timestamp delta from first call to import logger.
			level	-> Log level
			message	-> What you want to log
		'''
		self._initTime = time.time()
		if level is not None:
			self._level = level
		else:
			self._level = Level.DEBUG
		if f is not None:
			self.fd = f
		else:
			self.fd = sys.stderr
		if log_format is None:
			self._format = '[{clock}][{level}] {message}'
		else:
			self._format = log_format
		self.colorize = colorize and self.fd.isatty()
		if sys.platform.startswith('win') and self.colorize: # Windows wrapper.
			self.fd = AnsiToWin32(self.fd).stream
		self._log(Level.INFO, 'Logger initialized at %s' % time.asctime())

	def _log(self, level, message, _traceback = None):
		if level not in self._levelStr:
			raise ValueError('Non valid level code.')
		if level < self._level:
			return
		self.fd.write(self._colors[level])
		_t = time.time()
		_ms = int((_t - int(_t)) * 1000)
		_l = time.localtime()[:6] + (_ms, )
		_time = '%04d-%02d-%02d %02d:%02d:%02d.%03d' % _l
		_clock = '%13.6f' % (_t - self._initTime)
		_level = '%5s' % self._levelStr[level]
		_message = message
		finalMsg = self._format.format(time = _time, clock = _clock, level = _level, message = _message)
		self.fd.write(finalMsg)
		if not finalMsg.endswith('\n'):
			self.fd.write('\n')
		self.fd.write(Style.RESET_ALL)
		if level == Level.FATAL:
			self._backTrace(_traceback)
			sys.exit(1)

	def _backTrace(self, _frames = None):
		if _frames is None:
			_frames = traceback.extract_stack()[:-3][::-1]
		else:
			_frames = traceback.extract_tb(_frames)
		_depth = 0
		self._log(Level.TRACE, 'CallStack BackTrace:')
		for _frame in _frames:
			_code = _frame[3]
			if _code is None:
				_code = ''
			self._log(Level.TRACE, 'Trace #%d: %s' % (_depth, _code))
			self._log(Level.TRACE, '  Caller   : ' + _frame[2])
			self._log(Level.TRACE, '  Location : ' + _frame[0] + (':%d' % _frame[1]))
			_depth += 1

	def _exceptHandler(self, _type, value, traceback):
		_msg = ''
		if hasattr(value, 'message') and value.message:
			_msg = value.message
		elif hasattr(value, 'args') and value.args:
			_msg = ', '.join(map(str, value.args))
		elif hasattr(value, '__str__'):
			_msg = value.__str__()
		self._log(Level.FATAL, 'Unexpected exception: [%s] %s' % (_type.__name__, _msg), traceback)

	def _setLevel(self, level):
		if level not in self._levelStr:
			self._log(Level.WARN, 'Invalid logging level.')
			return
		self._level = level
		self._log(Level.DEBUG, 'Log level has changed to ' + self._levelStr[level])

_instance = None

def debug(message):
	_instance._log(Level.DEBUG, message)

def info(message):
	_instance._log(Level.INFO, message)

def warn(message):
	_instance._log(Level.WARN, message)

def error(message):
	_instance._log(Level.ERROR, message)

def fatal(message):
	_instance._log(Level.FATAL, message)

def stackTrace():
	_instance._backTrace()

def setLevel(level):
	_instance._setLevel(level)

def _exceptionHandler(_type, _value, _traceback):
	_instance._exceptHandler(_type, _value, _traceback)

def init():
	global _instance
	if _instance is None:
		_instance = _logger()
		sys.excepthook = _exceptionHandler

init()

