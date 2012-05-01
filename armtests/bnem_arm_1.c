#include <stdlib.h>
#include <stm32f4xx.h>
#include <stm32f4xx_gpio.h>
#include <stm32f4xx_rcc.h>
#include <stm32f4xx_usart.h>
#include "bnem.h"
// 112 KB SRAM
BIGNUM_LOCAL (x, BITS (192));	// first test operand
BIGNUM_LOCAL (y, BITS (192));	// second test operand
BIGNUM_LOCAL (m, BITS (192));	// modulus
BIGNUM_LOCAL (r, BITS (192));	// first result (e.g. remainder)
BIGNUM_LOCAL (q, BITS (192));	// second result (e.g. quotient)
BN_CTX *ctx;
int code;

volatile unsigned char inbuf [256];
volatile unsigned char otbuf [256];	// warning: good for hex output of 1024 bits, tops
volatile unsigned char inq, inx;
volatile unsigned char otq, otx;

static const unsigned char hex[16] = "0123456789abcdef";

//----------------------------------------------------------
#define THIS_USART	USART1

void USART1_IRQHandler (void) __attribute__ ((interrupt ("IRQ")));
void USART1_IRQHandler (void)
{
	if (USART_GetITStatus (THIS_USART, USART_IT_RXNE)) {
		inbuf[inq++] = USART_ReceiveData (THIS_USART);
	}
	
	if (USART_GetITStatus (THIS_USART, USART_IT_TXE)) {
		if (otq != otx)	// .. send another character from the buffer
			USART_SendData (THIS_USART, otbuf[otx++]);
		else			// .. ignore tx-ready interrupts
			USART_ITConfig (THIS_USART, USART_IT_TXE, DISABLE);
	}
} // USART1_IRQHandler

int serial_getc ()
{
	if (inq == inx)
		return -1;
	return inbuf[inx++];
} // serial_getc

void serial_putc (unsigned char c)
{
	otbuf[otq++] = c;
	USART_ITConfig (THIS_USART, USART_IT_TXE, ENABLE);
} // serial_putc

void serial_puts (const char *s)
{
	if (s && *s) {
		serial_putc (*(s++));
		while (*s)
			otbuf[otq++] = *(s++);
		USART_ITConfig (THIS_USART, USART_IT_TXE, ENABLE);
	}
} // serial_puts

void serial_put_hex (unsigned char c)
{
	serial_putc (hex[c >> 4]);
	serial_putc (hex[c & 0xF]);
} // serial_put_hex

void serial_put_hexint (int i)
{
	unsigned v = (unsigned)i;
	unsigned char buf [sizeof(unsigned)*2], *b;
	if (!v) {
		serial_putc ('0');
		return;
	}
	b = buf;
	while (v) {	// convert to low-endian string of hexdigits
		*(b++) = v & 0xF;
		v >>= 4;
	}
	do {	// output in high-endian order
		serial_putc (hex[*(--b)]);
	} while (b != buf);
} // serial_put_hex

//----------------------------------------------------------
void setup (void)
{
	{ // Set up random-number generator ..
	}
	
	{ // Set up serial communication ..
		GPIO_InitTypeDef gpio_init = {.GPIO_Mode=GPIO_Mode_AF};
		USART_InitTypeDef usart_init = {.USART_BaudRate=9600
				, .USART_WordLength=USART_WordLength_8b
				, .USART_StopBits=USART_StopBits_1, .USART_Parity=USART_Parity_No
				, .USART_Mode=USART_Mode_Rx|USART_Mode_Tx
				, .USART_HardwareFlowControl=USART_HardwareFlowControl_None};
		RCC_APB2PeriphClockCmd (RCC_APB2Periph_USART1, ENABLE);
		RCC_AHB1PeriphClockCmd (RCC_AHB1Periph_GPIOA, ENABLE);
		GPIO_PinAFConfig (GPIOA, GPIO_PinSource0, GPIO_AF_USART1);
		GPIO_Init (GPIOA, &gpio_init);
		USART_Init (THIS_USART, &usart_init);
		USART_Cmd (THIS_USART, ENABLE);
		USART_ITConfig (THIS_USART, USART_IT_RXNE, ENABLE);
		USART_ITConfig (THIS_USART, USART_IT_TXE, DISABLE);
		inq = inx = 0;
		otq = otx = 0;
	}
} // setup

//----------------------------------------------------------

int hexify_buf (unsigned char *bufp, unsigned char *endp)
{
	unsigned char *qp, *xp;
	qp = xp = bufp;
	if ((endp - bufp) & 1) {	// buffer holds an odd number of bytes
		qp++, xp++;	// first buffered byte has its correct hex value
	}
	while (xp < endp) {
		unsigned char c = *(xp++);
		*(qp++) = (c << 4) | *(xp++);
	}
	return qp - bufp;	// number of bytes converted
} // hexify_buf

void send_bignum (BIGNUM *bn, char label)
{
	int i;
	for (i=bn->top; i; i--) {	// send big-endian
		serial_put_hexint (bn->d[i-1]);
		serial_putc (',');
	}
	serial_putc (label);	// indicate result or remainder
} // send_bignum

void send_results (int code, BIGNUM* result1, BIGNUM* result2)
{
	serial_puts ("\n=");
	serial_put_hexint (code);	// send operation status
	serial_putc ('S');
	if (result1) {			// send first result
		send_bignum (result1, 'R');
	}
	if (result2) {			// send second result
		send_bignum (result2, 'Q');
	}
	serial_putc ('\n');
} // send_results

#define BUFSIZE	512
void process_char (unsigned char c)
{
	int hexcount;
	static unsigned char hexbuf [BUFSIZE], *bufp=hexbuf;
	switch (c) {
	case 'A': case 'B': case 'C': case 'D': case 'E': case 'F':
		c += 'a' - 'A';	// convert to lower case
		// fall through
	case 'a': case 'b': case 'c': case 'd': case 'e': case 'f':
		c = c - 'a' + '0' + 10;	// 'a' becomes '0'+10, etc.
		// fall through
	case '0': case '1': case '2': case '3': case '4':
	case '5': case '6': case '7': case '8': case '9':
		if (bufp - hexbuf < BUFSIZE)
			*(bufp++) = c - '0';	// binary value of this hex digit into big-endian buffer
		break;
		
	case 'X':	// Enter X operand
		hexcount = hexify_buf (hexbuf, bufp);
		BN_bin2bn (hexbuf, hexcount, &x);
		bufp = hexbuf;
		break;
	case 'Y':	// Enter Y operand
		hexcount = hexify_buf (hexbuf, bufp);
		BN_bin2bn (hexbuf, hexcount, &y);
		bufp = hexbuf;
		break;
	case 'M':	// Enter Modulus field
		hexcount = hexify_buf (hexbuf, bufp);
		BN_bin2bn (hexbuf, hexcount, &m);
		bufp = hexbuf;
		break;
	case '!':	// Clear input
		bufp = hexbuf;
		break;
	case '+':
		code = BN_add (&r, &x, &y);
		send_results (code, &r, NULL);
		break;
	case '-':
		code = BN_sub (&r, &x, &y);
		send_results (code, &r, NULL);
		break;
	case '*':
		code = BN_mul (&r, &x, &y, ctx);
		send_results (code, &r, NULL);
		break;
	case '/':
		code = BN_div (&q, &r, &x, &y, ctx);
		send_results (code, &r, &q);
		break;
	case '^':
		code = BN_mod_exp (&r, &x, &y, &m, ctx);
		send_results (code, &r, NULL);
		break;
	case '=':	// verify operand values
		serial_puts ("\n=");
		send_bignum (&x, 'X');
		send_bignum (&y, 'Y');
		send_bignum (&m, 'M');
		serial_putc ('\n');
		break;
	
	case '?':	// identify test
		serial_puts ("\nbnem_arm_1.c\n");
		break;
	case ' ': case '\t': case '\n':	// intentional no-op
		break;
	default:	// ignore all other input
		break;
	} // switch c
} // process_char

void main (void) __attribute__ ((noreturn));
void main (void)
{
	setup();
	ctx = BN_CTX_new();
	process_char ('!');	// initialize input processing
	for (;;) {
		int c;
		if ((c = serial_getc()) >= 0) {
			serial_putc (c);		// echo input
			process_char (c);
		}
	}
} // main
