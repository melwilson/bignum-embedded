#include <stdint.h>
#include <stdlib.h>
#ifndef C_DEBUG
#define C_DEBUG	0
#endif
#include <bnem.h>

// Fill in a bad random number implementation until the application links in a better one..
uint32_t bnem_random_word () __attribute__ ((weak));
uint32_t bnem_random_word ()
{
	return (uint32_t)(rand()) << 16 ^ (uint32_t)(rand());
} // bnem_random_word

// Extended Euclidean algorithm, Knuth's Algorithm X
int bnem_xgcd (BIGNUM *rx, BIGNUM *ry, const BIGNUM *a, const BIGNUM *b, BN_CTX *ctx)
{
	int result = 0;	// default return value is failure
	BIGNUM x, y, lastx, lasty, q, r, t1, t2, wa, wb;
	BN_init (&x);
	BN_init (&y);
	BN_init (&lastx);
	BN_init (&lasty);
	BN_init (&q);
	BN_init (&r);
	BN_init (&t1);
	BN_init (&t2);
	BN_init (&wa);
	BN_init (&wb);
	if ( ! BN_copy (&wa, a)) goto err;
	if ( ! BN_copy (&wb, b)) goto err;
	/*
	x, lastx = 0, 1
	y, lasty = 1, 0
	while b:
		q, r = divmod (a, b)
		a, b = b, r
		x, lastx = (lastx - q*x), x
		y, lasty = (lasty - q*y), y
	return lastx, lasty
	*/
	BN_one (&lastx);
	BN_one (&y);
	while ( ! BN_is_zero (&wb)) {
		if ( ! BN_div (&q, &r, &wa, &wb, ctx)) goto err;
		if ( ! BN_copy (&wa, &wb)) goto err;
		if ( ! BN_copy (&wb, &r)) goto err;
		
		if ( ! BN_copy (&t1, &x)) goto err;
		if ( ! BN_mul (&t2, &q, &x, ctx)) goto err;
		if ( ! BN_sub (&x, &lastx, &t2)) goto err;
		if ( ! BN_copy (&lastx, &t1)) goto err;
		
		if ( ! BN_copy (&t1, &y)) goto err;
		if ( ! BN_mul (&t2, &q, &y, ctx)) goto err;
		if ( ! BN_sub (&y, &lasty, &t2)) goto err;
		if ( ! BN_copy (&lasty, &t1)) goto err;
	}
	if (rx) { if ( ! BN_copy (rx, &lastx)) goto err; }
	if (ry) { if ( ! BN_copy (ry, &lasty)) goto err; }
	result = 1;	// result is success
err:
	BN_clear_free (&x);
	BN_clear_free (&y);
	BN_clear_free (&lastx);
	BN_clear_free (&lasty);
	BN_clear_free (&q);
	BN_clear_free (&r);
	BN_clear_free (&t1);
	BN_clear_free (&t2);
	BN_clear_free (&wa);
	BN_clear_free (&wb);
	return result;
} // bnem_xgcd
