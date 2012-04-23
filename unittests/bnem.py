#!/usr/bin/env python3.1
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
		value, factor = 0, 1
		for w in self.datawords():
			value += w * factor
			factor *= 0x100000000
		if self.neg:
			value = -value
		return value
			
def library (path=''):
	'''Set up a bignum shared library for testing.'''
	if not path:
		path = "../libbnem.so"
	libbnem = ctypes.CDLL (path)

	libbnem. BN_init .argtypes = [ctypes.POINTER (BignumType)]	# not so useful -- clears a struct bignum_st to zero
	libbnem. BN_new .restype = ctypes.POINTER (BignumType)	# allocate a new BIGNUM with empty data array
	libbnem. BN_value_one .argtypes = []						# allocate a new BIGNUM with value set to 1
	libbnem. BN_value_one .restype = ctypes.POINTER (BignumType)	# allocate a new BIGNUM with value set to 1
	
	libbnem. BN_bin2bn .argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER (BignumType)]
	libbnem. BN_bin2bn .restype = ctypes.POINTER (BignumType)
	
	libbnem. BN_add .argtypes = [ctypes.POINTER (BignumType), ctypes.POINTER (BignumType), ctypes.POINTER (BignumType)]
	libbnem. BN_add .restype = ctypes.c_int
	
	libbnem. BN_sub .argtypes = [ctypes.POINTER (BignumType), ctypes.POINTER (BignumType), ctypes.POINTER (BignumType)]
	libbnem. BN_sub .restype = ctypes.c_int
	
	libbnem. BN_mul .argtypes = [ctypes.POINTER (BignumType), ctypes.POINTER (BignumType), ctypes.POINTER (BignumType), ctypes.c_voidp]
	libbnem. BN_mul .restype = ctypes.c_int

	libbnem. BN_CTX_new .argtypes = []
	libbnem. BN_CTX_new .restype = ctypes.c_voidp
	return libbnem


if __name__ == '__main__':
	p1 = libbnem.BN_new()
	print (p1)
	v1 = p1.contents
	print (v1)
	print (v1.top, v1.dmax, v1.neg, v1.flags)
