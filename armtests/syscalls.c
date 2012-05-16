/* for caddr_t (typedef char * caddr_t;) */
#include <sys/types.h>
#include <errno.h>

#define DEBUG

//~ extern int  __HEAP_START;
extern unsigned char __bss_end__[];	// defined in linker script

#ifdef DEBUG
unsigned int _sbrk_call_count = 0;		// for debugging
unsigned char *_sbrk_prev_heap;
int _sbrk_last_incr = -1;
#endif

static unsigned int __get_MSP (void)
{
	register unsigned int __regMainStackPointer asm ("sp");
	return __regMainStackPointer;
}

caddr_t _sbrk ( int incr )
{
	static unsigned char *heap = NULL;
	unsigned char *prev_heap;

	if (heap == NULL) {
		heap = (unsigned char *)__bss_end__;
	}
	prev_heap = heap;
#ifdef DEBUG
	_sbrk_call_count++;
	_sbrk_prev_heap = heap;
	_sbrk_last_incr = incr;
#endif // DEBUG
	if (heap + incr >  (unsigned char*)__get_MSP()) {
		errno = ENOMEM;
		return  (caddr_t) -1;
	}
	heap += incr;

	return (caddr_t) prev_heap;
} // _sbrk
