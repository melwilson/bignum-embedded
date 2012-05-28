/* Copyright 2012 Mel Wilson, mwilson@melwilsonsoftware.ca
;* File Name          : startup_stm32f4xx.s
;* Author             : Mel Wilson
;* Version            : V1.0.0
;* Date               : Wed Apr 18 10:09:33 EDT 2012
;* Description        : STM32F4xx devices vector table.
;*                      After Reset the CortexM4 processor is in Thread mode,
;*                      priority is Privileged, the Stack is set to Main,
;*			and the HSI (16 MHz) is used as system clock source.
;*                      This module performs:
;*                      - Set the initial SP
;*                      - Set the initial PC == Reset_Handler
;*                      - Set the vector table entries with the exceptions ISR address
;*                      -  Call SysInit to configure the system clock and the external SRAM mounted on
;*                        STM324xG-EVAL board to be used as data memory (optional,
;*                        to be enabled by user)
;*                      - Branch to __main in the C library (which eventually
;*                        calls main()).
;* Documents :
* 			ARM White Paper: ARM Cortex-M3 Processor Software Development for ARM7TDMI Processor Programmers
***********************************************************/
.syntax unified
.thumb

/* Symbols provided by this module ... */
.global	__Vectors			/* vector 0 in generated vectors */
.global	__Vectors_End		/* limit address of generated vectors */
.global	__Vectors_Size		/* size in bytes of generated vector table */

/* Symbols from outside, mainly the linker script ... */
.extern	_etext		/* -> .data initial values in ROM */
.extern	_data		/* -> .data area in RAM */
.extern	_edata		/* end of .data area */
.extern	__bss_start	/* -> .bss area in RAM */
.extern	__bss_end__	/* end of .bss area */
.extern	__stack		/* top of stack */

#define ROM_RUN
.set CPP_SUPPORT, 0


/* Vector Table Mapped to Address 0 at Reset */
                /*AREA    RESET, DATA, READONLY*/
.section	.text

__Vectors:	
	.word	__stack	/* Top of Stack  */
	.word	Reset_Handler			/* Reset Handler */
	.word	NMI_Handler 			/* NMI Handler */
	.word	HardFault_Handler		/* Hard Fault Handler */
	.word	MemManage_Handler	/* MPU Fault Handler */
	.word	BusFault_Handler		/* Bus Fault Handler */
	.word	UsageFault_Handler		/* Usage Fault Handler */
	.word	0           	/* Reserved */
	.word	0           	/* Reserved */
	.word	0           	/* Reserved */
	.word	0           	/* Reserved */
	.word	SVC_Handler 		/* SVCall Handler */
	.word	DebugMon_Handler	/* Debug Monitor Handler */
	.word	0           	/* Reserved */
	.word	PendSV_Handler	/* PendSV Handler */
	.word	SysTick_Handler	/* SysTick Handler */

 	/* External Interrupts */
	.word	WWDG_IRQHandler    	/* Window WatchDog */
	.word	PVD_IRQHandler     		/* PVD through EXTI Line detection */
	.word	TAMP_STAMP_IRQHandler	/* Tamper and TimeStamps through the EXTI line */
	.word	RTC_WKUP_IRQHandler	/* RTC Wakeup through the EXTI line  */
	.word	FLASH_IRQHandler   	/* FLASH */
	.word	RCC_IRQHandler     	/* RCC */
	.word	EXTI0_IRQHandler   	/* EXTI Line0 */
	.word	EXTI1_IRQHandler   	/* EXTI Line1 */
	.word	EXTI2_IRQHandler   	/* EXTI Line2 */
	.word	EXTI3_IRQHandler   	/* EXTI Line3 */
	.word	EXTI4_IRQHandler   	/* EXTI Line4 */
	.word	DMA1_Stream0_IRQHandler	/* DMA1 Stream 0 */
	.word	DMA1_Stream1_IRQHandler	/* DMA1 Stream 1 */
	.word	DMA1_Stream2_IRQHandler	/* DMA1 Stream 2 */
	.word	DMA1_Stream3_IRQHandler	/* DMA1 Stream 3 */
	.word	DMA1_Stream4_IRQHandler	/* DMA1 Stream 4 */
	.word	DMA1_Stream5_IRQHandler	/* DMA1 Stream 5 */
	.word	DMA1_Stream6_IRQHandler	/* DMA1 Stream 6 */
	.word	ADC_IRQHandler     		/* ADC1, ADC2 and ADC3s */
	.word	CAN1_TX_IRQHandler 	/* CAN1 TX */
	.word	CAN1_RX0_IRQHandler	/* CAN1 RX0 */
	.word	CAN1_RX1_IRQHandler	/* CAN1 RX1 */
	.word	CAN1_SCE_IRQHandler	/* CAN1 SCE */
	.word	EXTI9_5_IRQHandler 	/* External Line[9:5]s */
	.word	TIM1_BRK_TIM9_IRQHandler		/* TIM1 Break and TIM9 */
	.word	TIM1_UP_TIM10_IRQHandler		/* TIM1 Update and TIM10 */
	.word	TIM1_TRG_COM_TIM11_IRQHandler	/* TIM1 Trigger and Commutation and TIM11 */
	.word	TIM1_CC_IRQHandler 			/* TIM1 Capture Compare */
	.word	TIM2_IRQHandler    	/* TIM2 */
	.word	TIM3_IRQHandler    	/* TIM3 */
	.word	TIM4_IRQHandler    	/* TIM4 */
	.word	I2C1_EV_IRQHandler 	/* I2C1 Event */
	.word	I2C1_ER_IRQHandler 	/* I2C1 Error */
	.word	I2C2_EV_IRQHandler 	/* I2C2 Event */
	.word	I2C2_ER_IRQHandler 	/* I2C2 Error */
	.word	SPI1_IRQHandler    	/* SPI1 */
	.word	SPI2_IRQHandler    	/* SPI2 */
	.word	USART1_IRQHandler  	/* USART1 */
	.word	USART2_IRQHandler  	/* USART2 */
	.word	USART3_IRQHandler  	/* USART3 */
	.word	EXTI15_10_IRQHandler 	/* External Line[15:10]s */
	.word	RTC_Alarm_IRQHandler 	/* RTC Alarm (A and B) through EXTI Line  */
	.word	OTG_FS_WKUP_IRQHandler 	/* USB OTG FS Wakeup through EXTI line */
	.word	TIM8_BRK_TIM12_IRQHandler		/* TIM8 Break and TIM12 */
	.word	TIM8_UP_TIM13_IRQHandler		/* TIM8 Update and TIM13 */
	.word	TIM8_TRG_COM_TIM14_IRQHandler	/* TIM8 Trigger and Commutation and TIM14 */
	.word	TIM8_CC_IRQHandler 			/* TIM8 Capture Compare */
	.word	DMA1_Stream7_IRQHandler	/* DMA1 Stream7 */
	.word	FSMC_IRQHandler    	/* FSMC */
	.word	SDIO_IRQHandler    	/* SDIO */
	.word	TIM5_IRQHandler    	/* TIM5 */
	.word	SPI3_IRQHandler    	/* SPI3 */
	.word	UART4_IRQHandler   	/* UART4 */
	.word	UART5_IRQHandler   	/* UART5 */
	.word	TIM6_DAC_IRQHandler	/* TIM6 and DAC1&2 underrun errors */
	.word	TIM7_IRQHandler    		/* TIM7 */
	.word	DMA2_Stream0_IRQHandler	/* DMA2 Stream 0 */
	.word	DMA2_Stream1_IRQHandler	/* DMA2 Stream 1 */
	.word	DMA2_Stream2_IRQHandler	/* DMA2 Stream 2 */
	.word	DMA2_Stream3_IRQHandler	/* DMA2 Stream 3 */
	.word	DMA2_Stream4_IRQHandler	/* DMA2 Stream 4 */
	.word	ETH_IRQHandler     		/* Ethernet */
	.word	ETH_WKUP_IRQHandler	/* Ethernet Wakeup through EXTI line */
	.word	CAN2_TX_IRQHandler 	/* CAN2 TX */
	.word	CAN2_RX0_IRQHandler	/* CAN2 RX0 */
	.word	CAN2_RX1_IRQHandler	/* CAN2 RX1 */
	.word	CAN2_SCE_IRQHandler	/* CAN2 SCE */
	.word	OTG_FS_IRQHandler  	/* USB OTG FS */
	.word	DMA2_Stream5_IRQHandler	/* DMA2 Stream 5 */
	.word	DMA2_Stream6_IRQHandler	/* DMA2 Stream 6 */
	.word	DMA2_Stream7_IRQHandler	/* DMA2 Stream 7 */
	.word	USART6_IRQHandler  	/* USART6 */
	.word	I2C3_EV_IRQHandler 	/* I2C3 event */
	.word	I2C3_ER_IRQHandler 	/* I2C3 error */
	.word	OTG_HS_EP1_OUT_IRQHandler	/* USB OTG HS End Point 1 Out */
	.word	OTG_HS_EP1_IN_IRQHandler	/* USB OTG HS End Point 1 In */
	.word	OTG_HS_WKUP_IRQHandler 	/* USB OTG HS Wakeup through EXTI */
	.word	OTG_HS_IRQHandler  	/* USB OTG HS */
	.word	DCMI_IRQHandler    		/* DCMI */
	.word	CRYP_IRQHandler    		/* CRYP crypto */
	.word	HASH_RNG_IRQHandler	/* Hash and Rng */
	.word	FPU_IRQHandler     	/* FPU */
__Vectors_End:
	.equ __Vectors_Size,  __Vectors_End - __Vectors


	.section	.text,"x"

/* Reset handler */
	.thumb_func
Reset_Handler:	.func	Reset_Handler
	.global	Reset_Handler
_start:	.global	_start
/* Right after Reset, the processor is in Privileged Level in Thread Mode */

/* ??? Set up memory mapping ??? */
/* ??? Initialize Interrupt System ??? */

/* ----------------------------------------------------- */
/* Copy initialized data to its execution address in RAM */
#ifdef ROM_RUN
	/* Move data initialization values to SRAM */
	/*ldr   r1,=_etext*/		/* -> ROM data start */
	/*ldr   r2,=_data*/		/* -> data start */
	ldr   r1,=__data_load		/* -> ROM data start */
	ldr   r2,=__data_start	/* -> data start */
	ldr   r3,=_edata	/* -> end of data */
1:	cmp   r2,r3		/* check if data to move */
	bhs	2f			/* - none left - continue */
	ldr	r0,[r1],#4	/* copy 4 bytes */
	str	r0,[r2],#4
	b	1b			/* loop until done */
2:
#endif

	/* Clear .bss */
        mov	r0,#0			/* get a zero */
        ldr	r1,=__bss_start		/* -> bss start */
        ldr	r2,=__bss_end__ 	/* -> bss end */
1:	cmp	r1,r2			/* check if data to clear */
	bhs	2f				/* - none left - continue */
        str	r0,[r1],#4		/* clear 4 bytes */
        b	1b				/* loop until done */
2:

#if 1
	/* mark unused stack space */
        ldr	r0,=0xDEADBEEF	/* marker value */
        ldr	r1,=__bss_end__	/* -> bss end */
        ldr	r2,=__stack 		/* -> end of free space */
1:	cmp	r1,r2			/* check if data to mark */
	bhs	2f				/* - none left - continue */
        str	r0,[r1],#4		/* clear 4 bytes */
        b	1b				/* loop until done */
2:
#endif

.if CPP_SUPPORT
/*
   Call C++ constructors (for objects in "global scope")
   ctor loop added by Martin Thomas 4/2005 
   based on a Anglia Design example-application for ST ARM
*/
	LDR 	r0, =__ctors_start__
	LDR 	r1, =__ctors_end__
ctor_loop:
	CMP	r0, r1
	BEQ	ctor_end
	LDR	r2, [r0], #4
	STMFD	sp!, {r0-r1}
	MOV		lr, pc		/* set return address */
	MOV		pc, r2		/* run the constructor code */
	LDMFD 	sp!, {r0-r1}
	B 		ctor_loop
ctor_end:
.endif /* CPP_SUPPORT */
/* Code above has done anything SystemInit might be needed for, right?
	LDR	%r0, =SystemInit
	BLX	%r0
*/
	LDR	%r0, =main
	BLX	%r0
	.endfunc	/* end of ResetHandler */
	
	
/* Dummy Exception Handlers (infinite loops which can be overridden) */
/* Define overridable handlers ... */
.macro	weak_handler label
	.thumb_func
\label:	.func	\label
	.weak	\label
	B	.
	.endfunc
.endm

	weak_handler	NMI_Handler
	weak_handler	HardFault_Handler
	weak_handler	MemManage_Handler
	weak_handler	BusFault_Handler
	weak_handler	UsageFault_Handler
	weak_handler	SVC_Handler
	weak_handler	DebugMon_Handler
	weak_handler	PendSV_Handler
	weak_handler	SysTick_Handler

/* Define weakly-linked labels ... */
.macro	weak_alias label
	.thumb_func
\label:
	.weak	\label
.endm

	.thumb_func
Default_Handler:	.func	Default_Handler
	weak_alias	WWDG_IRQHandler   
	weak_alias	PVD_IRQHandler    
	weak_alias	TAMP_STAMP_IRQHandler
	weak_alias	RTC_WKUP_IRQHandler  
	weak_alias	FLASH_IRQHandler  
	weak_alias	RCC_IRQHandler    
	weak_alias	EXTI0_IRQHandler  
	weak_alias	EXTI1_IRQHandler  
	weak_alias	EXTI2_IRQHandler  
	weak_alias	EXTI3_IRQHandler  
	weak_alias	EXTI4_IRQHandler  
	weak_alias	DMA1_Stream0_IRQHandler
	weak_alias	DMA1_Stream1_IRQHandler
	weak_alias	DMA1_Stream2_IRQHandler
	weak_alias	DMA1_Stream3_IRQHandler
	weak_alias	DMA1_Stream4_IRQHandler
	weak_alias	DMA1_Stream5_IRQHandler
	weak_alias	DMA1_Stream6_IRQHandler
	weak_alias	ADC_IRQHandler    
	weak_alias	CAN1_TX_IRQHandler
	weak_alias	CAN1_RX0_IRQHandler  
	weak_alias	CAN1_RX1_IRQHandler  
	weak_alias	CAN1_SCE_IRQHandler  
	weak_alias	EXTI9_5_IRQHandler
	weak_alias	TIM1_BRK_TIM9_IRQHandler
	weak_alias	TIM1_UP_TIM10_IRQHandler
	weak_alias	TIM1_TRG_COM_TIM11_IRQHandler 
	weak_alias	TIM1_CC_IRQHandler
	weak_alias	TIM2_IRQHandler   
	weak_alias	TIM3_IRQHandler   
	weak_alias	TIM4_IRQHandler   
	weak_alias	I2C1_EV_IRQHandler
	weak_alias	I2C1_ER_IRQHandler
	weak_alias	I2C2_EV_IRQHandler
	weak_alias	I2C2_ER_IRQHandler
	weak_alias	SPI1_IRQHandler   
	weak_alias	SPI2_IRQHandler   
	weak_alias	USART1_IRQHandler 
	weak_alias	USART2_IRQHandler 
	weak_alias	USART3_IRQHandler 
	weak_alias	EXTI15_10_IRQHandler 
	weak_alias	RTC_Alarm_IRQHandler 
	weak_alias	OTG_FS_WKUP_IRQHandler 
	weak_alias	TIM8_BRK_TIM12_IRQHandler
	weak_alias	TIM8_UP_TIM13_IRQHandler
	weak_alias	TIM8_TRG_COM_TIM14_IRQHandler
	weak_alias	TIM8_CC_IRQHandler
	weak_alias	DMA1_Stream7_IRQHandler
	weak_alias	FSMC_IRQHandler   
	weak_alias	SDIO_IRQHandler   
	weak_alias	TIM5_IRQHandler   
	weak_alias	SPI3_IRQHandler   
	weak_alias	UART4_IRQHandler  
	weak_alias	UART5_IRQHandler  
	weak_alias	TIM6_DAC_IRQHandler  
	weak_alias	TIM7_IRQHandler   
	weak_alias	DMA2_Stream0_IRQHandler
	weak_alias	DMA2_Stream1_IRQHandler
	weak_alias	DMA2_Stream2_IRQHandler
	weak_alias	DMA2_Stream3_IRQHandler
	weak_alias	DMA2_Stream4_IRQHandler
	weak_alias	ETH_IRQHandler    
	weak_alias	ETH_WKUP_IRQHandler  
	weak_alias	CAN2_TX_IRQHandler
	weak_alias	CAN2_RX0_IRQHandler  
	weak_alias	CAN2_RX1_IRQHandler  
	weak_alias	CAN2_SCE_IRQHandler  
	weak_alias	OTG_FS_IRQHandler 
	weak_alias	DMA2_Stream5_IRQHandler
	weak_alias	DMA2_Stream6_IRQHandler
	weak_alias	DMA2_Stream7_IRQHandler
	weak_alias	USART6_IRQHandler 
	weak_alias	I2C3_EV_IRQHandler
	weak_alias	I2C3_ER_IRQHandler
	weak_alias	OTG_HS_EP1_OUT_IRQHandler
	weak_alias	OTG_HS_EP1_IN_IRQHandler
	weak_alias	OTG_HS_WKUP_IRQHandler 
	weak_alias	OTG_HS_IRQHandler 
	weak_alias	DCMI_IRQHandler   
	weak_alias	CRYP_IRQHandler   
	weak_alias	HASH_RNG_IRQHandler  
	weak_alias	FPU_IRQHandler
	
	B       .	/* catch unexpected external interrupts */
        .endfunc /* Default_Handler */
	

	.align
	.end
