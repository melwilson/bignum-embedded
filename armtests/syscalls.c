/* for caddr_t (typedef char * caddr_t;) */
#include <sys/types.h>

//~ extern int  __HEAP_START;
extern unsigned char __bss_end__[];

caddr_t _sbrk ( int incr )
{
	static unsigned char *heap = NULL;
	unsigned char *prev_heap;

	if (heap == NULL) {
		//~ heap = (unsigned char *)&__HEAP_START;
		heap = (unsigned char *)__bss_end__;
	}
	prev_heap = heap;
	/* check removed to show basic approach */

	heap += incr;

	return (caddr_t) prev_heap;
} // _sbrk
