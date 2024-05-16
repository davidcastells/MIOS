CC=$(SOPC_KIT_NIOS2)/bin/gnu/H-x86_64-pc-linux-gnu/bin/nios2-elf-gcc
OBJDUMP=$(SOPC_KIT_NIOS2)/bin/gnu/H-x86_64-pc-linux-gnu/bin/nios2-elf-objdump
ELF2HEX=$(SOPC_KIT_NIOS2)/bin/elf2hex

all: testLEDBus.elf

clean:
	rm -f *.elf
	rm -f *.hex
	rm -f *.disasm

hex: testLEDBus.hex

disasm: testLEDBus.disasm

testLEDBus.elf: testLEDBus.c
	$(CC) testLEDBus.c -o testLEDBus.elf -ffunction-sections -T testLEDBus.ld -nostdlib
	


testLEDBus.disasm: testLEDBus.elf
	$(OBJDUMP) -d testLEDBus.elf > testLEDBus.disasm

testLEDBus.hex: testLEDBus.elf
	$(ELF2HEX) testLEDBus.elf --width=8 --base=0x0 --end=0x144

