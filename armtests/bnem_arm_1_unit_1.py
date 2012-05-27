#!/usr/bin/env python
# -*- coding: ASCII -*-
import getopt, random, re, serial, sys
import unittest

MAXBITS = 192		# significant bits in a bignum that is too big for test hardware
MAXBIG = pow (2, MAXBITS)	# Bignum that is too big for test hardware as operand or result
result_pattern = re.compile (r'''\n*=(?P<status>[0-9a-f]*)S(?P<errno>[0-9a-f,]*)E(?:(?P<r>-?[0-9a-f,]*)R)?(?:(?P<q>-?[0-9a-f,]*)Q)?\n''')
verify_pattern = re.compile (r'''\n*=(?:(?P<x>-?[0-9a-f,]*)X)?(?:(?P<y>-?[0-9a-f,]*)Y)?(?:(?P<m>-?[0-9a-f,]*)M)?\n''')

def hex_to_bignum (s):
	'''Convert big-endian hex value from reply to int.'''
	val = v1 = 0
	neg = False
	if s.startswith ('-'):
		neg = True
		s = s[1:]
		
	if not s:
		return 0
		
	if ',' not in s:
		val = int (s, 16)
	else:
		for c in s:
			if c == ',':
				val = val * (1<<32) + v1
				v1 = 0
			elif c in '0123456789abcdef':
				v1 = v1 * 16 + int (c, 16)
	if neg:
		val = -val
	return val
	
def parse_results (results):
	'''Convert the hex result string from the test board to numeric values.'''
	m = result_pattern.match (results)
	if m is None:
		return m
	values = {}
	d = m.groupdict()
	for k in ('status', 'r', 'q'):
		v = d[k]
		if v is not None:
			values[k] = hex_to_bignum (d[k])
	return values
	
def parse_verify (results):
	'''Convert the hex result string from the test board to numeric values.'''
	m = verify_pattern.match (results)
	if m is None:
		return m
	values = {}
	d = m.groupdict()
	for k in ('x', 'y', 'm'):
		v = d[k]
		if v is not None:
			values[k] = hex_to_bignum (d[k])
	return values
	
def calculation_test (input):
	'''Send a calculation to the test board and return the reply.'''
	reply = []
	conn.write (input)
	while 1:
		c = conn.read (1)
		if c == '\n':
			break
	while 1:
		c = conn.read (1)
		reply.append (c)
		if c == '\n':
			break
	return ''.join (reply)


def random_ulong ():
	return random.randint (0, 0xFFFFFFFF)
	
def random_big ():
	#~ return random.randint (0x100000000, 0x1FFFFFFFFFFFFFFFF)
	return random.randint (MAXBIG/4, MAXBIG-1)
	
def random_medium ():
	return random.randint (pow (2, 64), pow (2, 96)-1)

#-----------------------------------------------------------
class TestCreate (unittest.TestCase):
	'''Test BIGNUM creation and initialization.'''
	longMessage = True
	setting_template = '!%xX%xY%xM='
	
	def test_create_1 (self):
		'''Test BN setting in test appliance.'''
		for i in xrange (10):
			x = random_big()
			y = random_big()
			m = random_big()
			
			# test in sections, because = sends back a very large reply
			# and the test hardware only buffers 256 bytes
			request = self.setting_template % (x, 1, 2)
			reply = calculation_test (request)
			results = parse_verify (reply)
			self.assertEqual (results['x'], x, 'x: expected %d, actual %d\nRequest: %s\tReply: %s' % (x, results['x'], request, reply))
			self.assertEqual (results['y'], 1, '\nRequest: %s\tReply: %s' % (request, reply))
			self.assertEqual (results['m'], 2, '\nRequest: %s\tReply: %s' % (request, reply))
			
			request = self.setting_template % (1, y, 2)
			reply = calculation_test (request)
			results = parse_verify (reply)
			self.assertEqual (results['x'], 1, '\nRequest: %s\tReply: %s' % (request, reply))
			self.assertEqual (results['y'], y, 'y: expected %d, actual %d\nRequest: %s\tReply: %s' % (y, results['y'], request, reply))
			self.assertEqual (results['m'], 2, '\nRequest: %s\tReply: %s' % (request, reply))
			
			request = self.setting_template % (1, 2, m)
			reply = calculation_test (request)
			results = parse_verify (reply)
			self.assertEqual (results['x'], 1, '\nRequest: %s\tReply: %s' % (request, reply))
			self.assertEqual (results['y'], 2, '\nRequest: %s\tReply: %s' % (request, reply))
			self.assertEqual (results['m'], m, 'm: expected %d, actual %d\nRequest: %s\tReply: %s' % (m, results['m'], request, reply))
	
		
class BignumTest (unittest.TestCase):
	'''Ancestor class for arithmetic tests.'''
		
class TestAdd (BignumTest):
	'''Test simple addition.'''
	addition_template = '!%xX%xY+'
	
	def test_add (self):
		'''Test BN_add.'''
		request = self.addition_template % (5, 512)
		reply = calculation_test (request)
		results = parse_results (reply)
		self.assertEqual (results['status'], 1)
		self.assertEqual (results['r'], 517)
		print '\ntest_add:\t%s\t%s' % (request, reply)
		
	#~ def test_add_word (self):
		#~ '''Random tests of BN_add_word.'''
		#~ ap = lbn.BN_new()
		#~ for i in range (10):
			#~ av = random_big()
			#~ bv = random_ulong()
			#~ set_intval (ap, av)
			#~ code = lbn.BN_add_word (ap, bv)
			#~ self.assertEqual (code, 1)
			#~ self.assertEqual (ap.contents.python_int(), av+bv)
	
class TestSub (BignumTest):
	'''Test simple subtraction.'''
	subtraction_template = '!%xX%xY-'
	
	def test_sub_1 (self):
		'''Test BN_sub, small numbers.'''
		request = self.subtraction_template % (5, 2)
		reply = calculation_test (request)
		results = parse_results (reply)
		self.assertEqual (results['status'], 1)
		self.assertEqual (results['r'], 3)
	
	def test_sub_2 (self):
		'''Test BN_sub, larger numbers.'''
		request = self.subtraction_template % (0x100000005, 0x100000002)
		reply = calculation_test (request)
		results = parse_results (reply)
		self.assertEqual (results['status'], 1)
		self.assertEqual (results['r'], 3)
		
	#~ def test_sub_word (self):
		#~ '''Random tests of BN_sub_word.'''
		#~ ap = lbn.BN_new()
		#~ for i in range (10):
			#~ av = random_big()
			#~ bv = random_ulong()
			#~ set_intval (ap, av)
			#~ code = lbn.BN_sub_word (ap, bv)
			#~ self.assertEqual (code, 1)
			#~ self.assertEqual (ap.contents.python_int(), av-bv)
		
class TestMul (BignumTest):
	'''Test simple multiplication.'''
	multiplication_template = '!%xX%xY*'
	errmsg_template = "Actual %s, expected %s\nRequest:%s\tReply:%s\n"
	def random_factor (self): return random.randint (pow (2, MAXBITS/8), pow (2, MAXBITS/2)-1)
	
	def test_mul_1 (self):
		'''Test small numbers.'''
		request = self.multiplication_template % (3, 5)
		reply = calculation_test (request)
		results = parse_results (reply)
		self.assertEqual (results['status'], 1)
		self.assertEqual (results['r'], 15)
		
		#~ lbn.BN_set_negative (bp, True)
		#~ code = lbn.BN_mul (rp, ap, bp, ctx)
		#~ self.assertEqual (code, 1)
		#~ self.assertEqual (rp.contents.python_int(), -15)
		
		#~ lbn.BN_set_negative (ap, True)
		#~ code = lbn.BN_mul (rp, ap, bp, ctx)
		#~ self.assertEqual (code, 1)
		#~ self.assertEqual (rp.contents.python_int(), 15)
	
	def test_mul_2 (self):
		'''Test large numbers.'''
		case_count = 0
		for i in range (10):
			av = self.random_factor()
			bv = self.random_factor()
			request = self.multiplication_template % (av, bv)
			reply = calculation_test (request)
			results = parse_results (reply)
			self.assertEqual (results['status'], 1)
			self.assertEqual (results['r'], av*bv
					, self.errmsg_template % (results['r'], av*bv, request, reply))
			case_count += 1
		print '\ntest_mul_2 ran %d cases.' % (case_count,)
		
	#~ def test_mul_word (self):
		#~ '''Random tests of BN_mul_word.'''
		#~ ap = lbn.BN_new()
		#~ for i in range (10):
			#~ av = random_big()
			#~ bv = random_ulong()
			#~ set_intval (ap, av)
			#~ code = lbn.BN_mul_word (ap, bv)
			#~ self.assertEqual (code, 1)
			#~ self.assertEqual (ap.contents.python_int(), av*bv)
			
class TestDiv (BignumTest):
	'''Test simple division.'''
	division_template = '!%xX%xY/'
	errmsg_template = "%s actual %s, expected %s\nRequest:%s\tReply:%s\n"
	
	def one_divide_test (self, dividend, divisor, message=''):
		if divisor > dividend:
			divisor, dividend = dividend, divisor
		request = self.division_template % (dividend, divisor)
		reply = calculation_test (request)
		results = parse_results (reply)
		q, r = divmod (dividend, divisor)
		self.assertEqual (results['status'], 1)
		self.assertEqual (results['q'], q, message + self.errmsg_template % ('q', results['q'], q, request, reply))
		self.assertEqual (results['r'], r, message + self.errmsg_template % ('r', results['r'], r, request, reply))
	
	def test_div_1 (self):
		'''Test small numbers.'''
		request = self.division_template % (15, 1)
		reply = calculation_test (request)
		results = parse_results (reply)
		self.assertEqual (results['status'], 1)
		self.assertEqual (results['q'], 15)
		self.assertEqual (results['r'], 0)
		print '\ntest_div_1:\t%s\t%s' % (request, reply)
		
		request = self.division_template % (15, 2)
		reply = calculation_test (request)
		results = parse_results (reply)
		self.assertEqual (results['status'], 1)
		self.assertEqual (results['q'], 7)
		self.assertEqual (results['r'], 1)
		
		#~ lbn.BN_set_negative (drp, True)
		#~ code = lbn.BN_div (qp, rp, ddp, drp, ctx)
		#~ self.assertEqual (code, 1)
		#~ self.assertEqual (qp.contents.python_int(), -7)
		#~ self.assertEqual (rp.contents.python_int(), 1)
		
	def test_div_2 (self):
		'''Division of medium-sized numbers.'''
		case_count = 0
		for i in range (20):
			dividend = random_medium()
			divisor = random_medium()
			self.one_divide_test (dividend, divisor)
			case_count += 1
		print '\ntest_div_2 ran %d cases.' % (case_count,)
		
	def test_div_3 (self):
		'''Division of medium-sized numbers.'''
		case_count = 0
		for i in range (20):
			dividend = random.randint (pow (2, 96), pow (2, 128)-1)
			divisor = random.randint (pow (2, 48), pow (2, 112)-1)
			self.one_divide_test (dividend, divisor)
			case_count += 1
		print '\ntest_div_3 ran %d cases.' % (case_count,)


	def test_div_4 (self):
		'''Division of medium-sized numbers.'''
		case_count = 0
		for i in range (20):
			dividend = random.randint (pow (2, 128), pow (2, 160)-1)
			divisor = random.randint (pow (2, 64), pow (2, 148)-1)
			self.one_divide_test (dividend, divisor)
			case_count += 1
		print '\ntest_div_4 ran %d cases.' % (case_count,)
		
	def test_div_to160 (self):
		'''Random tests of division.'''
		case_count = 0
		for i in range (20):
			#~ dividend = random.randint (pow (2, 128), pow (2, 160)-1)	# all tests in this range succeed
			#~ divisor = random.randint (pow (2, 64), pow (2, 148)-1)
			dividend = random.randint (pow (2, 128), pow (2, 160)-1)	# all tests in this range succeed
			divisor = random.randint (pow (2, 64), pow (2, 160)-1)
			self.one_divide_test (dividend, divisor, '#%d:\t' % (case_count,))
			case_count += 1
		print '\ntest_div_5 ran %d cases.' % (case_count,)
		
	def test_div_to161 (self):
		'''Random tests of division.'''
		case_count = 0
		for i in range (20):
			dividend = random.randint (pow (2, 160), pow (2, 161)-1)	# most tests in this range fail
			divisor = random.randint (pow (2, 64), pow (2, 161)-1)
			self.one_divide_test (dividend, divisor, '#%d:\t' % (case_count,))
			case_count += 1
		print '\ntest_div_5 ran %d cases.' % (case_count,)
		

class TestModExp (BignumTest):
	'''Test  modular exponentiation.'''
	exponentiation_template = '!%xX%xY%xM^'
	errmsg_template = "%s actual %s, expected %s\nRequest:%s\tReply:%s\n"
	
	def test_modexp_1 (self):
		'''Test small values.'''
		av = 3
		pv = 4
		mv = 5
		request = self.exponentiation_template % (av, pv, mv)
		reply = calculation_test (request)
		results = parse_results (reply)
		r = pow (av, pv, mv)
		self.assertEqual (results['status'], 1)
		self.assertEqual (results['r'], r, self.errmsg_template % ('r', results['r'], r, request, reply))
		print '\ntest_modexp_1:\t%s\t%s' % (request, reply)
		
	def test_modexp_2 (self):
		'''Test large values.'''
		case_count = 0
		for i in range (10):	# random tests
			av = random_big()
			pv = random_ulong()
			mv = random_big()
			request = self.exponentiation_template % (av, pv, mv)
			reply = calculation_test (request)
			results = parse_results (reply)
			print '\ntest_modexp_2:\t%s\t%s' % (request, reply)
			r = pow (av, pv, mv)
			self.assertEqual (results['status'], 1, '#%d:\t' % (case_count,) + self.errmsg_template % ('status', results['status'], 1, request, reply))
			self.assertEqual (results['r'], r, '#%d:\t' % (case_count,) + self.errmsg_template % ('r', results['r'], r, request, reply))
			case_count += 1
		

#-----------------------------------------------------------
port = '/dev/ttyUSB0'
baudrate = 9600
opts, args = getopt.getopt (sys.argv[1:], 'b:p:', ['baud=', 'port='])
for o, v in opts:
	if o in ('-b', '--baud'):
		baudrate = int (v)
	elif o in ('-p', '--port'):
		port = v
conn = serial.Serial (port, baudrate)
unittest.main()
conn.close()
