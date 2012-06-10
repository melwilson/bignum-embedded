#include <bnem.h>
#include <stdint.h>

#ifndef C_DEBUG
#define C_DEBUG	0
#endif
#if C_DEBUG
#include <stdio.h>
#include <errno.h>
#endif // C_DEBUG

int bnem_possibly_prime (BIGNUM *np)
{
	BIGNUM q, n1, x, y;
	BN_CTX *ctx;
	uint32_t j, k;
	int result = -1;	// error indication is the default
	
	BN_init (&q);
	BN_init (&n1);
	BN_init (&x);
	BN_init (&y);
	if ( ! (ctx = BN_CTX_new()) ) goto err;
	
	if ( ! BN_copy (&n1, np) ) goto err;
	if ( ! BN_sub_word (&n1, 1) ) goto err;
	if ( ! BN_copy (&q, &n1) ) goto err;
	k = 0;
	
	result = -2;
	while ( ! BN_is_odd (&q)) {
		result = -3;
		if (BN_div_word (&q, 2) < 0) goto err;
		k++;
	}
	// Now n == pow (2, k) * q + 1
	
	result = -4;
	if ( ! bnem_random (&x, n1.top) ) goto err;
	if ( ! BN_mod (&x, &x, &n1, ctx) ) goto err;
	if ( ! BN_mod_exp (&y, &x, &q, np, ctx) ) goto err;
	if (BN_is_one (&y)  ||  BN_cmp (&y, &n1) == 0) {
		result = 1;	// n is possibly prime
		goto end;
	}
	result = -5;
	for (j=1; j < k; j++) {
		if ( ! BN_mod_sqr (&y, &y, np, ctx) ) goto err;
		if (BN_is_one (&y)) {
			result = 0;	// n is not prime
			goto end;
		}
		if (BN_cmp (&y, &n1) == 0) {
			result = 1;	// n is possibly prime
			goto end;
		}
	}
	result = 0;	// n is not prime
end:
err:
	BN_CTX_free (ctx);
	BN_free (&q);
	BN_free (&n1);
	BN_free (&x);
	BN_free (&y);
	return result;
} // bnem_possibly_prime

int bnem_is_prime (BIGNUM *np, int confidence)
{
	int code, i;
	if (confidence < 1)
		confidence = 25;	// fill in a default confidence value
	for (i=0; i < confidence; i++) {
		code = bnem_possibly_prime (np);
		if (code == 0) {
			return 0;	// can't be prime
		}
		else if (code < 0) {	// computation error
#if C_DEBUG
			//~ fprintf (stderr, "Error calling bnem_possibly_prime %d\t errno %d\tbnem_errno %d\n", code, errno, bn_errno);
			fprintf (stderr, "Error calling bnem_possibly_prime %d\t errno %d\n", code, errno);
#endif // C_DEBUG
			return 0;
		}
	}
	return 1;
} // bnem_is_prime

BIGNUM *bnem_random_prime (BIGNUM *r, int bits)
{
	BIGNUM *rw;
	int word_count = (bits + 31) / 32;
	if (r)
		rw = r;
	else
		rw = BN_new();
	bnem_random (rw, word_count);
	BN_set_bit (rw, 0);
	BN_set_bit (rw, bits-1);
	while (! bnem_is_prime (rw, -1)) {
		// 734 tries to avoid a bias toward the primes with the widest gaps below them
		BN_add_word (rw, 734);
		if (rw->top > word_count)
			BN_div_word (rw, 2);
	}
	return rw;
} // bnem_random_prime
