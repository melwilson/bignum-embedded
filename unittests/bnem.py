#!/usr/bin/env python3.1
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
			
	def python_int (self):
		'''Return this bignum's value as a Python integer.'''
		value, factor = 0, 1
		for j in range (self.top):
			value += self.d[j] * factor
			factor *= 4294967296
		if self.neg:
			value = -value
		return value
			
def library (path=''):
	'''Set up a bignum shared library for testing.'''
	if not path:
		path = "../libbnem.so"
	libbnem = ctypes.CDLL (path)

	libbnem.BN_new.restype = ctypes.POINTER (BignumType)
	libbnem.BN_value_one.restype = ctypes.POINTER (BignumType)
	
	libbnem.BN_add.argtypes = [ctypes.POINTER (BignumType), ctypes.POINTER (BignumType), ctypes.POINTER (BignumType)]
	libbnem.BN_add.restype = ctypes.c_int
	
	libbnem.BN_mul.argtypes = [ctypes.POINTER (BignumType), ctypes.POINTER (BignumType), ctypes.POINTER (BignumType), ctypes.c_voidp]
	libbnem.BN_mul.restype = ctypes.c_int

	libbnem.BN_CTX_new.restype = ctypes.c_voidp
	return libbnem


if __name__ == '__main__':
	p1 = libbnem.BN_new()
	print (p1)
	v1 = p1.contents
	print (v1)
	print (v1.top, v1.dmax, v1.neg, v1.flags)
