CC=$(SOPC_KIT_NIOS2)/bin/gnu/H-x86_64-pc-linux-gnu/bin/nios2-elf-gcc
OBJDUMP=$(SOPC_KIT_NIOS2)/bin/gnu/H-x86_64-pc-linux-gnu/bin/nios2-elf-objdump
ELF2HEX=$(SOPC_KIT_NIOS2)/bin/elf2hex

all: testLEDCI.elf

clean:
	rm -f *.elf
	rm -f *.hex
	rm -f *.disasm

hex: testLEDCI.hex

disasm: testLEDCI.disasm

testLEDCI.elf: testLEDCI.c
	$(CC) testLEDCI.c -o testLEDCI.elf -ffunction-sections -T testLEDCI.ld -nostdlib
	


testLEDCI.disasm: testLEDCI.elf
	$(OBJDUMP) -d testLEDCI.elf > testLEDCI.disasm

testLEDCI.hex: testLEDCI.elf
	$(ELF2HEX) testLEDCI.elf --width=8 --base=0x0 --end=0x144

