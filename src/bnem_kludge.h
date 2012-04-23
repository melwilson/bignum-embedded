#ifndef BNEM_KLUDGE_H_
#define BNEM_KLUDGE_H_

extern unsigned int bn_errno;
//~ #define BNerr(org,code)	(bn_errno = code)
	
// kludge out some OPENSSL specials
#define OPENSSL_malloc	malloc
#define OPENSSL_free	free
//~ #define BN_BLINDING_free	free

#define assert(x)
#define OPENSSL_assert(x)

#define CRYPTO_r_lock(lock)
#define CRYPTO_r_unlock(lock)
#define CRYPTO_w_lock(lock)
#define CRYPTO_w_unlock(lock)
#define CRYPTO_THREADID_current(x)
#define CRYPTO_THREADID	unsigned long

#endif // BNEM_KLUDGE_H_
