#!/usr/bin/env python3.1
import bnem
import unittest

class TestCreate (unittest.TestCase):
	'''Test BIGNUM creation and initialization.'''
	lbn = bnem.library()
	
	def test1 (self):
		lbn = self.lbn
		bnp = lbn.BN_new()
		bn = bnp.contents
		self.assertEqual (bn.top, 0)
		
		onep = lbn.BN_value_one()
		onev = onep.contents
		self.assertEqual (onev.python_int(), 1)
		
	def test_bin2bn (self):
		'''Test initialization of BIGNUM from big-endian byte string.'''
		lbn = self.lbn
		ap = lbn.BN_new()
		bin2 = b"\x02"
		bp = lbn.BN_bin2bn (bin2, len (bin2), ap)
		self.assertEqual (bp.contents.python_int(), 2)
		bin259 = b"\x01\x03"	# high-endian 256+3
		bp = lbn.BN_bin2bn (bin259, len (bin259), ap)
		self.assertEqual (ap.contents.python_int(), 259)
		self.assertEqual (bp.contents.python_int(), 259)
		
		cp = lbn.BN_new()
		bin30005 = b"\x03\x00\x00\x00\x05"
		dp = lbn.BN_bin2bn (bin30005, len (bin30005), cp)
		self.assertEqual (dp.contents.datalist(), [0x5, 0x3])	# verify contents of low-endian data array
		self.assertEqual (cp.contents.python_int(), 0x300000005)

class TestAdd (unittest.TestCase):
	'''Test simple addition.'''
	lbn = bnem.library()
	
	def test_add (self):
		'''Test BN_add.'''
		lbn = self.lbn
		bin5 = b"\x05"
		ap = lbn.BN_new()
		lbn.BN_bin2bn (bin5, len (bin5), ap)
		self.assertEqual (ap.contents.python_int(), 5)
		
		bin512 = b"\x02\x00"
		bp = lbn.BN_new()
		lbn.BN_bin2bn (bin512,  len (bin512), bp)
		self.assertEqual (bp.contents.python_int(), 512)
		
		rp = lbn.BN_new()
		code = lbn.BN_add (rp, ap, bp)
		self.assertEqual (code, 1)
		self.assertEqual (rp.contents.python_int(), 517)
		
class TestSub (unittest.TestCase):
	'''Test simple subtraction.'''
	lbn = bnem.library()
	
	def a_bignum (self, binval):
		'''Create a bignum from a value given in a big-endian bytestring.'''
		bnp = self.lbn.BN_new()
		self.lbn.BN_bin2bn (binval, len (binval), bnp)
		return bnp
	
	def test_sub_1 (self):
		'''Test BN_sub, small numbers.'''
		
		bin5 = b"\x05"
		bin2 = b"\x02"
		ap = self.a_bignum (bin5)
		bp = self.a_bignum (bin2)
		rp = self.lbn.BN_new()
		code = self.lbn.BN_sub (rp, ap, bp)
		self.assertEqual (code, 1)
		self.assertEqual (rp.contents.python_int(), 3)
		
		sp = self.lbn.BN_new()
		code = self.lbn.BN_sub (sp, bp, ap)
		self.assertEqual (code, 1)
		self.assertEqual (sp.contents.python_int(), -3)
	
	def test_sub_2 (self):
		'''Test BN_sub, larger numbers.'''
		
		bin5 = b"\x01\x00\x00\x00\x05"
		bin2 = b"\x01\x00\x00\x00\x02"
		ap = self.a_bignum (bin5)
		bp = self.a_bignum (bin2)
		rp = self.lbn.BN_new()
		code = self.lbn.BN_sub (rp, ap, bp)
		self.assertEqual (code, 1)
		self.assertEqual (rp.contents.python_int(), 3)
		
		sp = self.lbn.BN_new()
		code = self.lbn.BN_sub (sp, bp, ap)
		self.assertEqual (code, 1)
		self.assertEqual (sp.contents.python_int(), -3)

unittest.main()
