#!/usr/bin/env python3.1
# -*- coding: ASCII -*-
import bnem		# ctypes interface to the bignum-embedded shared library
import random
import unittest

lbn = bnem.library ("../libbnem-i386-32.so")	# library under test

def random_ulong ():
	return random.randint (0, 0xFFFFFFFF)
	
def random_big ():
	return random.randint (0x100000000, 0x1FFFFFFFFFFFFFFFF)
	
def a_bignum (intval):
	'''Create a bignum equal to a given Python integer.'''
	bnp = lbn.BN_new()
	set_intval (bnp, intval)
	return bnp
		
def set_intval (bnp, intval):
	'''Set the value of a bignum from a Python integer.'''
	# Depends on BN_bin2bn and BN_set_negative working correctly.
	neg_flag = intval < 0
	if neg_flag:
		intval = -intval
	if not intval:
		bytevals = [0]
	else:
		bytevals = []
		while intval:	# convert integer to little-endian bytes
			intval, r = divmod (intval, 256)
			bytevals.append (r)
		bytevals.reverse()	# change to big-endian bytes
	byteval = bytes (bytevals)
	lbn.BN_bin2bn (byteval, len (byteval), bnp)
	lbn.BN_set_negative (bnp, neg_flag)

#-----------------------------------------------------------
class TestCreate (unittest.TestCase):
	'''Test BIGNUM creation and initialization.'''
	
	def test1 (self):
		'''Test creation.'''
		bnp = lbn.BN_new()
		bn = bnp.contents
		self.assertEqual (bn.top, 0)
		self.assertEqual (bn.python_int(), 0)
		
		onep = lbn.BN_value_one()
		self.assertEqual (onep.contents.python_int(), 1)
		
	def test_bin2bn (self):
		'''Test initialization of BIGNUM from big-endian byte string.'''
		ap = lbn.BN_new()
		bin2 = b"\x02"
		bp = lbn.BN_bin2bn (bin2, len (bin2), ap)
		self.assertEqual (bp.contents.python_int(), 2)
		bin259 = b"\x01\x03"	# high-endian 256+3
		bp = lbn.BN_bin2bn (bin259, len (bin259), ap)
		self.assertEqual (ap.contents.python_int(), 259)
		self.assertEqual (bp.contents.python_int(), 259)
		
		lbn.BN_set_negative (ap, True)
		self.assertEqual (ap.contents.python_int(), -259)
		
		lbn.BN_set_negative (ap, False)
		self.assertEqual (ap.contents.python_int(), 259)
		
		cp = lbn.BN_new()
		bin30005 = b"\x03\x00\x00\x00\x05"
		dp = lbn.BN_bin2bn (bin30005, len (bin30005), cp)
		self.assertEqual (dp.contents.datalist(), [0x5, 0x3])	# verify contents of low-endian data array
		self.assertEqual (cp.contents.python_int(), 0x300000005)
		
		#~ # The following cause a segmentation fault ..
		#~ lbn.BN_clear_free (ap)
		#~ lbn.BN_clear_free (bp)
		#~ lbn.BN_clear_free (cp)
		#~ lbn.BN_clear_free (dp)
		
	def test_set_word (self):
		'''Test initialization of BIGNUM from unsigned long int.'''
		ap = lbn.BN_new()
		code = lbn.BN_set_word (ap, 0)
		self.assertEqual (code, 1)
		self.assertEqual (ap.contents.python_int(), 0)
		for i in range (10):
			av = random.randint (1, 0xFFFFFFFF)
			code = lbn.BN_set_word (ap, av)
			self.assertEqual (code, 1)
			self.assertEqual (ap.contents.python_int(), av)
		
class BignumTest (unittest.TestCase):
	'''Ancestor class for arithmetic tests.'''
		
class TestAdd (BignumTest):
	'''Test simple addition.'''
	
	def test_add (self):
		'''Test BN_add.'''
		ap = a_bignum (5)
		self.assertEqual (ap.contents.python_int(), 5)
		
		bp = a_bignum (0x200)
		self.assertEqual (bp.contents.python_int(), 512)
		
		rp = lbn.BN_new()
		code = lbn.BN_add (rp, ap, bp)
		self.assertEqual (code, 1)
		self.assertEqual (rp.contents.python_int(), 517)
		
	def test_add_word (self):
		'''Randomized tests of BN_add_word.'''
		ap = lbn.BN_new()
		for i in range (10):
			av = random_big()
			bv = random_ulong()
			set_intval (ap, av)
			code = lbn.BN_add_word (ap, bv)
			self.assertEqual (code, 1)
			self.assertEqual (ap.contents.python_int(), av+bv)
	
class TestSub (BignumTest):
	'''Test simple subtraction.'''
	
	def test_sub_1 (self):
		'''Test BN_sub, small numbers.'''
		
		ap = a_bignum (5)
		bp = a_bignum (2)
		rp = lbn.BN_new()
		code = lbn.BN_sub (rp, ap, bp)
		self.assertEqual (code, 1)
		self.assertEqual (rp.contents.python_int(), 3)
		
		sp = lbn.BN_new()
		code = lbn.BN_sub (sp, bp, ap)
		self.assertEqual (code, 1)
		self.assertEqual (sp.contents.python_int(), -3)
	
	def test_sub_2 (self):
		'''Test BN_sub, larger numbers.'''
		
		ap = a_bignum (0x100000005)
		bp = a_bignum (0x100000002)
		rp = lbn.BN_new()
		code = lbn.BN_sub (rp, ap, bp)
		self.assertEqual (code, 1)
		self.assertEqual (rp.contents.python_int(), 3)
		
		sp = lbn.BN_new()
		code = lbn.BN_sub (sp, bp, ap)
		self.assertEqual (code, 1)
		self.assertEqual (sp.contents.python_int(), -3)
		
	def test_sub_word (self):
		'''Randomized tests of BN_sub_word.'''
		ap = lbn.BN_new()
		for i in range (10):
			av = random_big()
			bv = random_ulong()
			set_intval (ap, av)
			code = lbn.BN_sub_word (ap, bv)
			self.assertEqual (code, 1)
			self.assertEqual (ap.contents.python_int(), av-bv)
		
class TestMul (BignumTest):
	'''Test simple multiplication.'''
	
	def test_mul_1 (self):
		'''Test small numbers.'''
		ap = a_bignum (3)
		bp = a_bignum (5)
		rp = lbn.BN_new()
		ctx = lbn.BN_CTX_new()
		
		code = lbn.BN_mul (rp, ap, bp, ctx)
		self.assertEqual (code, 1)
		self.assertEqual (rp.contents.python_int(), 15)
		
		lbn.BN_set_negative (bp, True)
		code = lbn.BN_mul (rp, ap, bp, ctx)
		self.assertEqual (code, 1)
		self.assertEqual (rp.contents.python_int(), -15)
		
		lbn.BN_set_negative (ap, True)
		code = lbn.BN_mul (rp, ap, bp, ctx)
		self.assertEqual (code, 1)
		self.assertEqual (rp.contents.python_int(), 15)
	
	def test_mul_2 (self):
		'''Test large numbers.'''
		ctx = lbn.BN_CTX_new()
		ap = lbn.BN_new()
		bp = lbn.BN_new()
		rp = lbn.BN_new()
		for i in range (10):
			av = random_big()
			bv = random_big()
			set_intval (ap, av)
			set_intval (bp, bv)
			code = lbn.BN_mul (rp, ap, bp, ctx)
			self.assertEqual (code, 1)
			self.assertEqual (rp.contents.python_int(), av*bv)
			#~ print ('%s * %s = %s' % (av, bv, rp.contents.python_int()))
		
	def test_mul_word (self):
		'''Randomized tests of BN_mul_word.'''
		ap = lbn.BN_new()
		for i in range (10):
			av = random_big()
			bv = random_ulong()
			set_intval (ap, av)
			code = lbn.BN_mul_word (ap, bv)
			self.assertEqual (code, 1)
			self.assertEqual (ap.contents.python_int(), av*bv)
			#~ print ('%s * %s = %s' % (av, bv, ap.contents.python_int()))
			
class TestDiv (BignumTest):
	'''Test simple division.'''
	
	def test_div_1 (self):
		'''Test small numbers.'''
		ctx = lbn.BN_CTX_new()
		drp = lbn.BN_new()
		ddp = lbn.BN_new()
		qp = lbn.BN_new()
		rp = lbn.BN_new()
		
		dividend = 15
		divisor = 1
		set_intval (ddp, dividend)
		set_intval (drp, divisor)
		code = lbn.BN_div (qp, rp, ddp, drp, ctx)
		self.assertEqual (code, 1)
		self.assertEqual (qp.contents.python_int(), 15)
		self.assertEqual (rp.contents.python_int(), 0)
		
		divisor = 2
		set_intval (drp, divisor)
		code = lbn.BN_div (qp, rp, ddp, drp, ctx)
		self.assertEqual (code, 1)
		self.assertEqual (qp.contents.python_int(), 7)
		self.assertEqual (rp.contents.python_int(), 1)
		tq, tr = divmod (dividend, divisor)
		self.assertEqual (qp.contents.python_int(), tq)
		self.assertEqual (rp.contents.python_int(), tr)
		
		code = lbn.BN_div (qp, rp, drp, ddp, ctx)
		self.assertEqual (code, 1)
		self.assertEqual (qp.contents.python_int(), 0)
		self.assertEqual (rp.contents.python_int(), 2)
		
		lbn.BN_set_negative (drp, True)
		code = lbn.BN_div (qp, rp, ddp, drp, ctx)
		self.assertEqual (code, 1)
		self.assertEqual (qp.contents.python_int(), -7)
		self.assertEqual (rp.contents.python_int(), 1)
		#~ # Python divmod is not completely compatible with BN_div
		#~ tq, tr = divmod (15, -2)
		#~ self.assertEqual (qp.contents.python_int(), tq)
		#~ self.assertEqual (rp.contents.python_int(), tr)
		
	def test_div_2 (self):
		'''Randomized tests.'''
		ctx = lbn.BN_CTX_new()
		drp = lbn.BN_new()
		ddp = lbn.BN_new()
		qp = lbn.BN_new()
		rp = lbn.BN_new()
		for i in range (10):
			dividend = random_big()
			divisor = random_big()
			if divisor > dividend:
				divisor, dividend = dividend, divisor
			set_intval (ddp, dividend)
			set_intval (drp, divisor)
			code = lbn.BN_div (qp, rp, ddp, drp, ctx)
			self.assertEqual (code, 1)
			tq, tr = divmod (dividend, divisor)
			self.assertEqual (qp.contents.python_int(), tq)
			self.assertEqual (rp.contents.python_int(), tr)
			#~ print ('%s / %s = %s : %s' % (dividend, divisor, tq, tr))

class TestModExp (BignumTest):
	'''Test  modular exponentiation.'''
	def test_modexp_1 (self):
		rp = lbn.BN_new()
		ap = lbn.BN_new()
		pp = lbn.BN_new()
		mp = lbn.BN_new()
		ctx = lbn.BN_CTX_new()
		
		av = 3
		pv = 4
		mv = 5
		set_intval (ap, av)
		set_intval (pp, pv)
		set_intval (mp, mv)
		code = lbn.BN_mod_exp (rp, ap, pp, mp, ctx)
		self.assertEqual (code, 1)
		self.assertEqual (rp.contents.python_int(), pow (av, pv, mv))
		
		for i in range (10):	# random tests
			av = random_big()
			pv = random_ulong()
			mv = random_big()
			set_intval (ap, av)
			set_intval (pp, pv)
			set_intval (mp, mv)
			code = lbn.BN_mod_exp (rp, ap, pp, mp, ctx)
			self.assertEqual (code, 1)
			self.assertEqual (rp.contents.python_int(), pow (av, pv, mv))
			#~ print ('%s ** %s %% %s = %s' % (av, pv, mv, rp.contents.python_int()))
			
			
class TestPrimes (BignumTest):
	'''Test prime-number algos.'''
	def test_prime_1 (self):
		p1 = lbn.BN_new()
		q1 = lbn.bnem_random_prime (p1, 64)
		print ('Random prime (64):', int (p1.contents), int (q1.contents))
		# Note that ctypes does not have OOR (original object return), it constructs a new, equivalent object each time you retrieve an attribute:
		# so the following kinds of test can't work:
		#: self.assert_(p1 is q1)
		#: self.assert_(p1.contents is q1.contents)
		#: self.assert_(p1.contents == q1.contents)
		self.assert_(int (p1.contents) == int (q1.contents))
		
		p2 = lbn.BN_new()
		q2 = lbn.bnem_random_prime (p2, 32)
		print ('Random prime (32):', int (p2.contents), int (q2.contents))
		
		ctx = lbn.BN_CTX_new()
		n3 = lbn.BN_new()
		code = lbn.BN_mul (n3, p1, p2, ctx)
		self.assertEqual (code, 1)
		
		primecode = lbn.bnem_is_prime (p1, 25)
		self.assertEqual (primecode, 1)
		primecode = lbn.bnem_is_prime (n3, 25)
		self.assertEqual (primecode, 0)

#-----------------------------------------------------------
unittest.main()
