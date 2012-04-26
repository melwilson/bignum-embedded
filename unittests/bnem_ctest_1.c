#include "bnem.h"

#define BIGNUM_LOCAL(name,size)	BN_ULONG name##_words[size]; BIGNUM name = {.d=name##_words, .top=0, .dmax=size, .flags=BN_FLG_STATIC_DATA}

#define ULONG_BITS	((sizeof (BN_ULONG)) * 8)
#define BITS(bits)	((bits + ULONG_BITS - 1) / ULONG_BITS)


int test1 (void)
{
	BIGNUM_LOCAL (ab, BITS(800));
	int code;
	code = BN_set_word (&ab, 1);
	return code;
} // test1

int main (int argc, char *argv[])
{
	test1();
	return 0;
} // main
