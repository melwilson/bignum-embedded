#
# bnem_arm_1/Makefile
# Make the test for staticly allocated bignums
#
PROGRAM = bnem_arm_1

CROSS_PREFIX= /home/arm-cross/bin/arm-none-eabi-
CROSS_FLAGS= -mcpu=cortex-m4 -mthumb
CROSS_COMPILE= /home/arm-cross/lib/gcc/arm-none-eabi/4.6.1

LIBRARIES = -L/home/arm-cross/arm-none-eabi/lib/thumb2
LIBRARIES += -L/home/arm-cross/lib/gcc/arm-none-eabi/4.6.1/
PROJECTLIB = lib


PERIPH = $(PROJECTLIB)/STM32F4xx_StdPeriph_Driver

INCLUDES = -I$(CROSS_COMPILE)/include
INCLUDES += -I$(PROJECTLIB)/include
INCLUDES += -I$(PERIPH)/inc
INCLUDES += -I$(PROJECTLIB)/CMSIS/Include
INCLUDES += -I.

VPATH = $(PERIPH)/src
OPTIMIZATION= -Os

CC = $(CROSS_PREFIX)gcc
AS = $(CROSS_PREFIX)as
LD = $(CROSS_PREFIX)ld
SIZE = $(CROSS_PREFIX)size
STRIP = $(CROSS_PREFIX)strip
OBJCOPY = $(CROSS_PREFIX)objcopy

DEFINES= -D"assert_param(x)="
DEFINES += -D"HSE_VALUE=((uint32_t)8000000)"

#PERIPH = STM32F4xx_StdPeriph_Driver

#INCLUDES = -I$(CROSS_COMPILE)/include
#INCLUDES += -I/home/lib/arm/include/stm32f4
#INCLUDES += -I$(PERIPH)/inc
#INCLUDES += -I/home/lib/arm/STM32F4-Discovery_FW_V1.1.0/Libraries/CMSIS/Include
#INCLUDES += -I.

#LIBRARIES = -L/home/arm-cross/arm-none-eabi/lib/thumb2
#LIBRARIES += -L/home/arm-cross/lib/gcc/arm-none-eabi/4.6.1/

CFLAGS =  -c -Wall -mlong-calls -ffunction-sections
CFLAGS += $(CROSS_FLAGS)
CFLAGS += -g $(OPTIMIZATION) $(INCLUDES) $(DEFINES)
ASFLAGS =  -Wall  $(CROSS_FLAGS) -mthumb-interwork $(INCLUDES)
LDFLAGS = -g -static $(OPTIMIZATION) $(LIBRARIES) -Wl,--cref,--relax,-Map=$(PROGRAM).map,--gc-sections  -Tbnem_arm_1.x.ld


STMOBJECTS= stm32f4xx_gpio.o stm32f4xx_rcc.o stm32f4xx_rtc.o stm32f4xx_usart.o


all: $(PROGRAM).hex

$(PROGRAM).hex: startup_stm32f4xx.o system_stm32f4xx.o syscalls.o bnem_arm_1.o $(STMOBJECTS) libbnem-cortexm4.a
	$(CC)  $(LDFLAGS) -o $(PROGRAM).elf  $^
	$(OBJCOPY) -O ihex $(PROGRAM).elf $@

#~ %.hex : %.elf
	#~ $(OBJCOPY) -O ihex $< $@
	
#~ oldhex:
	#~ $(OBJCOPY) -O ihex -j .text $< $@
	
#~ $(PROGRAM).elf:  $(ASM_OBJECTS) $(C_OBJECTS)
	#~ $(CC) $(LDFLAGS) -o $@ $^


clean:
	rm -f *.o *.elf *.hex
	#~ -rm -f $(OBJ)/*.o $(BIN)/*.bin $(BIN)/*.elf
	
%.S: %.c
	$(CC) -S $(CFLAGS) -o $@ $^
	
asm: bnem_arm_1.S system_stm32f4xx.S

depend:
	@[ -n "$(MAKEDEPEND)" ] # should be set by upper Makefile...
	$(MAKEDEPEND) -- $(CFLAG) $(INCLUDES) $(DEPFLAG) -- $(PROGS) $(LIBSRC)

dclean:
	$(PERL) -pe 'if (/^# DO NOT DELETE THIS LINE/) {print; exit(0);}' $(MAKEFILE) >Makefile.new
	mv -f Makefile.new $(MAKEFILE)

# DO NOT DELETE THIS LINE -- make depend depends on it.

