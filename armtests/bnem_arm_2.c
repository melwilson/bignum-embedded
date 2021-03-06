// Excercise BN, explicitly using dynamic allocation
#include <stdlib.h>
#include <errno.h>
#include <stm32f4xx.h>
#include <stm32f4xx_gpio.h>
#include <stm32f4xx_rcc.h>
#include <stm32f4xx_usart.h>
#include "bnem.h"
 // Baud rate for serial commands ..
#define BAUD	9600
#define COMMAND_USART	USART2
// .. changeing the line above needs changes in setup and IRQ handler

// Use Discovery board Blinkenlights:
//~ #define LED_GREEN	PD12
//~ #define LED_ORANGE	PD13
//~ #define LED_RED	PD14
//~ #define LED_BLUE	PD15

// 112 KB SRAM
BIGNUM x;	// first test operand
BIGNUM y;	// second test operand
BIGNUM m;	// modulus
BIGNUM r;	// first result (e.g. remainder)
BIGNUM q;	// second result (e.g. quotient)
BN_CTX *ctx;
int code;

volatile unsigned char inbuf [256];
volatile unsigned char otbuf [256];	// warning: good for hex output of 1024 bits, tops
volatile unsigned char inq, inx;
volatile unsigned char otq, otx;

static const unsigned char hex[16] = "0123456789abcdef";

extern unsigned int _sbrk_call_count;	// for debugging
extern int _sbrk_last_incr;
extern unsigned char *_sbrk_prev_heap;
unsigned char idle_count=0;

RCC_ClocksTypeDef rcc_clocksfreq;

//----------------------------------------------------------
// .. changing the line above will mean big changes to setup() .

void USART2_IRQHandler (void) __attribute__ ((interrupt ("IRQ")));
void USART2_IRQHandler (void)
{
	if (USART_GetITStatus (COMMAND_USART, USART_IT_RXNE)) {
		inbuf[inq++] = USART_ReceiveData (COMMAND_USART);
	}
	
	if (USART_GetITStatus (COMMAND_USART, USART_IT_TXE)) {
		if (otq != otx)	// .. send another character from the buffer
			USART_SendData (COMMAND_USART, otbuf[otx++]);
		else			// .. ignore tx-ready interrupts
			USART_ITConfig (COMMAND_USART, USART_IT_TXE, DISABLE);
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
	USART_ITConfig (COMMAND_USART, USART_IT_TXE, ENABLE);
} // serial_putc

void serial_puts (const char *s)
{
	if (s && *s) {
		serial_putc (*(s++));
		while (*s)
			otbuf[otq++] = *(s++);
		USART_ITConfig (COMMAND_USART, USART_IT_TXE, ENABLE);
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
	{ // set up clock outputs for debugging ..
		GPIO_InitTypeDef gpio8_init = { .GPIO_Pin = GPIO_Pin_8
				, .GPIO_Mode = GPIO_Mode_AF
				, .GPIO_Speed = GPIO_Speed_100MHz
				, .GPIO_OType = GPIO_OType_PP
				, .GPIO_PuPd = GPIO_PuPd_NOPULL 
				};
		GPIO_InitTypeDef gpio9_init = { .GPIO_Pin = GPIO_Pin_9
				, .GPIO_Mode = GPIO_Mode_AF
				, .GPIO_Speed = GPIO_Speed_100MHz
				, .GPIO_OType = GPIO_OType_PP
				, .GPIO_PuPd = GPIO_PuPd_NOPULL 
				};
		RCC_AHB1PeriphClockCmd (RCC_AHB1Periph_GPIOA, ENABLE);
		RCC_AHB1PeriphClockCmd (RCC_AHB1Periph_GPIOC, ENABLE);
		GPIO_Init (GPIOA, &gpio8_init);
		GPIO_Init (GPIOC, &gpio9_init);
		RCC_MCO1Config (RCC_MCO1Source_PLLCLK, RCC_MCO1Div_4);
		RCC_MCO2Config (RCC_MCO2Source_SYSCLK, RCC_MCO2Div_4);
		GPIO_PinAFConfig (GPIOA, GPIO_PinSource8, GPIO_AF_MCO);
		GPIO_PinAFConfig (GPIOC, GPIO_PinSource9, GPIO_AF_MCO);
	}
	
	{ // Set up random-number generator ..
	}
	
	{ // Set up Blinkenlights ..
		GPIO_InitTypeDef gpiod_init = { .GPIO_Pin = 1<<12 | 1<<13 | 1<<14 | 1<<15
				, .GPIO_Mode = GPIO_Mode_OUT
				, .GPIO_Speed = GPIO_Speed_2MHz
				, .GPIO_OType = GPIO_OType_PP
				, .GPIO_PuPd = GPIO_PuPd_NOPULL 
				};
		RCC_AHB1PeriphClockCmd (RCC_AHB1Periph_GPIOD, ENABLE);
		GPIO_Init (GPIOD, &gpiod_init);
	}
	
	{ // Set up serial communication ..
		GPIO_InitTypeDef serial_gpio_init = {.GPIO_Pin = GPIO_Pin_2 | GPIO_Pin_3
				, .GPIO_Mode = GPIO_Mode_AF
				, .GPIO_Speed = GPIO_Speed_25MHz
				, .GPIO_OType = GPIO_OType_PP
				, .GPIO_PuPd = GPIO_PuPd_NOPULL 
				};
		USART_InitTypeDef usart_init = {.USART_BaudRate = BAUD
				, .USART_WordLength = USART_WordLength_8b
				, .USART_StopBits = USART_StopBits_1
				, .USART_Parity = USART_Parity_No
				, .USART_Mode = USART_Mode_Rx | USART_Mode_Tx
				, .USART_HardwareFlowControl = USART_HardwareFlowControl_None
				};
		RCC_APB1PeriphClockCmd (RCC_APB1Periph_USART2, ENABLE);
		RCC_AHB1PeriphClockCmd (RCC_AHB1Periph_GPIOA, ENABLE);
		GPIO_Init (GPIOA, &serial_gpio_init);
		GPIO_PinAFConfig (GPIOA, GPIO_PinSource2, GPIO_AF_USART2);
		GPIO_PinAFConfig (GPIOA, GPIO_PinSource3, GPIO_AF_USART2);
		USART_Init (COMMAND_USART, &usart_init);
				
		USART_Cmd (COMMAND_USART, ENABLE);
		USART_ITConfig (COMMAND_USART, USART_IT_RXNE, ENABLE);
		USART_ITConfig (COMMAND_USART, USART_IT_TXE, DISABLE);
		inq = 0;
		inx = 0;
		otq = 0;
		otx = 0;
	}
} // setup

//----------------------------------------------------------

// Pack a buffer full of bytes 0..0x0F into 0..0xFF
int pack_hexbuf (unsigned char *bufp, unsigned char *endp)
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
	return qp - bufp;	// number of resulting packed bytes
} // pack_hexbuf

void send_bignum (BIGNUM *bn, char label)
{
	int i;
	if (bn->neg)
		serial_putc ('-');
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
	serial_put_hexint (bn_errno);	// send error codes
	serial_putc (',');
	serial_put_hexint (errno);
	serial_putc ('E');
	if (result1) {			// send first result
		send_bignum (result1, 'R');
	}
	if (result2) {			// send second result
		send_bignum (result2, 'Q');
	}
	serial_putc ('\n');
} // send_results

void send_debug ()
{
	serial_puts ("\n_sbrk_call_count:\t");
	serial_put_hexint (_sbrk_call_count);
	serial_puts ("\n_sbrk_prev_heap:\t");
	serial_put_hexint ((int)_sbrk_prev_heap);
	serial_puts ("\n_sbrk_last_incr:\t");
	serial_put_hexint (_sbrk_last_incr);
	serial_putc ('\n');
} // send_debug

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
		hexcount = pack_hexbuf (hexbuf, bufp);
		BN_bin2bn (hexbuf, hexcount, &x);
		bufp = hexbuf;
		break;
	case 'Y':	// Enter Y operand
		hexcount = pack_hexbuf (hexbuf, bufp);
		BN_bin2bn (hexbuf, hexcount, &y);
		bufp = hexbuf;
		break;
	case 'M':	// Enter Modulus field
		hexcount = pack_hexbuf (hexbuf, bufp);
		BN_bin2bn (hexbuf, hexcount, &m);
		bufp = hexbuf;
		break;
	case '!':	// Clear input
		bufp = hexbuf;
		break;
	case '+':
		ERR_clear_error();
		errno = 0;
		code = BN_add (&r, &x, &y);
		send_results (code, &r, NULL);
		break;
	case '-':
		ERR_clear_error();
		errno = 0;
		code = BN_sub (&r, &x, &y);
		send_results (code, &r, NULL);
		break;
	case '*':
		ERR_clear_error();
		errno = 0;
		code = BN_mul (&r, &x, &y, ctx);
		send_results (code, &r, NULL);
		break;
	case '/':
		ERR_clear_error();
		errno = 0;
		code = BN_div (&q, &r, &x, &y, ctx);
		send_results (code, &r, &q);
		break;
	case '^':
		ERR_clear_error();
		errno = 0;
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
	
	case '"':	// identify test
		serial_puts ("\nbnem_arm_2.c\n");
		break;
	case '?':	// log debugging data
		send_debug();
		break;
	case ' ': case '\t': case '\n':	// intentional no-op
		break;
	default:	// ignore all other input
		break;
	} // switch c
} // process_char

extern void SystemInit (void);

void main (void) __attribute__ ((noreturn));
void main (void)
{
	static const unsigned char grey4[16] = {0x0, 0x1, 0x3, 0x2, 0x6, 0x7, 0x5, 0x4, 0xC, 0xD, 0xF, 0xE, 0xA, 0xB, 0x9, 0x8};
	SystemInit();
	setup();
	ctx = BN_CTX_new();
	BN_init (&x);
	BN_init (&y);
	BN_init (&m);
	BN_init (&r);
	BN_init (&q);
	RCC_GetClocksFreq (&rcc_clocksfreq);
	process_char ('!');	// initialize input processing
	NVIC_EnableIRQ (USART2_IRQn);
	for (;;) {
		unsigned char v;
		int c;
		if ((c = serial_getc()) >= 0) {
			process_char (c);
		}
		
		idle_count++;
		v = grey4[idle_count >> 4];
		GPIO_ResetBits (GPIOD, v << 12);
		GPIO_SetBits (GPIOD, ((~v) & 0xF) << 12);
	}
} // main
