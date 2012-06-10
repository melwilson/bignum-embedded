#!/usr/bin/env python3.1
# -*- coding: ASCII -*-
'''Arrange to access a shared-object version of the bignum library using Python ctypes.'''
import ctypes

class BignumType (ctypes.Structure):
	"""The structure that's manipulated by the bn library.
struct bignum_st {
	BN_ULONG *d;	/* Pointer to an array of 'BN_BITS2' bit chunks. */
	int top;	/* Index of last used d +1. */
	/* The next are internal book keeping for bn_expand. */
	int dmax;	/* Size of the d array. */
	int neg;	/* one if the number is negative */
	int flags;
};
"""
	_fields_ = [
			('d', ctypes.POINTER (ctypes.c_ulong)),
			('top', ctypes.c_int),
			('dmax', ctypes.c_int),
			('neg', ctypes.c_int),
			('flags', ctypes.c_int),
			]
			
	def __int__ (self):
		'''Return this bignum's value as a Python integer.'''
		value, factor = 0, 1
		for w in self.datawords():
			value += w * factor
			factor *= 0x100000000
		if self.neg:
			value = -value
		return value
			
	def datawords (self):
		'''Yield the words in the little-endian data array.'''
		return (self.d[k] for k in range (self.top))
		
	def datalist (self):
		'''Return a list of the words in the little-endian data array.'''
		return list (self.datawords())
		
	def hexval (self):
		'''Return a hex string representing the words in the little-endian data array.'''
		return ':'.join (hex (x) for x in self.datawords())
			
	def python_int (self):
		'''Return this bignum's value as a Python integer.'''
		return self.__int__()
			
def library (path):
	'''Set up a bignum shared library for testing.'''
	libbnem = ctypes.CDLL (path)
	
	bignum_pointer = ctypes.POINTER (BignumType)

	libbnem. BN_init .argtypes = [bignum_pointer]	# clears a struct bignum_st to zero
	libbnem. BN_new .restype = bignum_pointer	# allocate a new BIGNUM with empty data array
	libbnem. BN_value_one .argtypes = []						# access a constant BIGNUM with value 1
	libbnem. BN_value_one .restype = bignum_pointer	# access a constant BIGNUM with value 1
	libbnem. BN_set_word .argtypes = [bignum_pointer, ctypes.c_ulong]	# set the value of a BIGNUM
	libbnem. BN_set_word .restype = ctypes.c_int
	libbnem. BN_clear_free .argtypes = [bignum_pointer]	# release the memory allocated to a BIGNUM
	libbnem. BN_set_negative .argtypes = [bignum_pointer, ctypes.c_int]
	
	libbnem. BN_bin2bn .argtypes = [ctypes.c_char_p, ctypes.c_int, bignum_pointer]
	libbnem. BN_bin2bn .restype = bignum_pointer
	
	libbnem. BN_add .argtypes = [bignum_pointer, bignum_pointer, bignum_pointer]
	libbnem. BN_add .restype = ctypes.c_int
	libbnem. BN_add_word .argtypes = [bignum_pointer, ctypes.c_ulong]
	libbnem. BN_add_word .restype = ctypes.c_int
	
	libbnem. BN_sub .argtypes = [bignum_pointer, bignum_pointer, bignum_pointer]
	libbnem. BN_sub .restype = ctypes.c_int
	libbnem. BN_sub_word .argtypes = [bignum_pointer, ctypes.c_ulong]
	libbnem. BN_sub_word .restype = ctypes.c_int
	
	libbnem. BN_mul .argtypes = [bignum_pointer, bignum_pointer, bignum_pointer, ctypes.c_voidp]
	libbnem. BN_mul .restype = ctypes.c_int
	libbnem. BN_mul_word .argtypes = [bignum_pointer, ctypes.c_ulong]
	libbnem. BN_mul_word .restype = ctypes.c_int

	libbnem. BN_div .argtypes = [bignum_pointer, bignum_pointer	# quotient, remainder
			, bignum_pointer, bignum_pointer, ctypes.c_voidp]	# divisor, dividend, context
	libbnem. BN_div .restype = ctypes.c_int
	
	libbnem. BN_mod_exp .argtypes = [bignum_pointer	# result
			, bignum_pointer, bignum_pointer	# base, power
			, bignum_pointer, ctypes.c_voidp]	# modulus, context
	libbnem. BN_mod_exp .restype = ctypes.c_int


	libbnem. BN_CTX_new .argtypes = []
	libbnem. BN_CTX_new .restype = ctypes.c_voidp
	
#~ int bnem_is_prime (BIGNUM *np, int confidence);
#~ int bnem_possibly_prime (BIGNUM *np);
#~ int bnem_random (BIGNUM *result, int datasize);
#~ BIGNUM *bnem_random_prime (BIGNUM *r, int bits);
#~ int bnem_xgcd (BIGNUM *rx, BIGNUM *ry, const BIGNUM *a, const BIGNUM *b, BN_CTX *ctx);
	libbnem. bnem_is_prime .argtypes = [bignum_pointer, ctypes.c_int]
	libbnem. bnem_is_prime .restype = ctypes.c_int
	libbnem. bnem_possibly_prime .argtypes = [bignum_pointer]
	libbnem. bnem_possibly_prime .restype = ctypes.c_int
	libbnem. bnem_random .argtypes = [bignum_pointer, ctypes.c_int]
	libbnem. bnem_random .restype = ctypes.c_int
	libbnem. bnem_random_prime .argtypes = [bignum_pointer, ctypes.c_int]
	libbnem. bnem_random_prime .restype = bignum_pointer
	libbnem. bnem_xgcd .argtypes = [bignum_pointer, bignum_pointer, bignum_pointer, bignum_pointer, ctypes.c_voidp]
	libbnem. bnem_xgcd .restype = ctypes.c_int
	return libbnem


if __name__ == '__main__':
	libbnem = library ("../libbnem.so")
	p1 = libbnem.BN_new()
	print (p1)
	v1 = p1.contents
	print (v1)
	print (v1.top, v1.dmax, v1.neg, v1.flags)
	
	print ('POINTERs are shareable:', ctypes.POINTER (BignumType) is ctypes.POINTER (BignumType))
