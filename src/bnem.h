/* Copyright (c) 2012, Mel Wilson
All rights reserved.

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions 
are met:

    Redistributions of source code must retain the above copyright 
    notice, this list of conditions and the following disclaimer.
    Redistributions in binary form must reproduce the above copyright 
    notice, this list of conditions and the following disclaimer in the 
    documentation and/or other materials provided with the distribution.
    Neither the name of the <ORGANIZATION> nor the names of its 
    contributors may be used to endorse or promote products derived 
    from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND 
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, 
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF 
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, 
EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/
#ifndef BNEM_H_
#define BNEM_H_
#include <stdint.h>

#include <bnem_types.h>
#include "bnem_kludge.h"
#include <bn.h>

#define BIGNUM_LOCAL(label,size)	BN_ULONG label##_words[size]; BIGNUM label={.d=label##_words, .top=0, .dmax=(size), .neg=0, .flags=BN_FLG_STATIC_DATA}
#define BITS(n)	(((n) + sizeof(BN_ULONG)*8-1) / (sizeof(BN_ULONG) * 8))

typedef uint32_t bnem_random_word_t ();	// type of application-provided source of random word values

int bnem_is_prime (BIGNUM *np, int confidence);
int bnem_possibly_prime (BIGNUM *np);
int bnem_random (BIGNUM *result, int datasize);
BIGNUM *bnem_random_prime (BIGNUM *r, int bits);
int bnem_xgcd (BIGNUM *rx, BIGNUM *ry, const BIGNUM *a, const BIGNUM *b, BN_CTX *ctx);

#endif // BNEM_H_
