#include <bnem.h>
#include <stdint.h>

extern uint32_t bnem_random_word (void);
// Set result to a random value, `datasize` uint32_t s long.
int bnem_random (BIGNUM *result, int datasize)
{
	uint32_t bits[datasize];
	int i;
	for (i=0; i < datasize; i++) {
		bits[i] = bnem_random_word();
	}
	return (BIGNUM *)0 != BN_bin2bn ((unsigned char *)bits, datasize * sizeof (uint32_t), result);
} // big_random

