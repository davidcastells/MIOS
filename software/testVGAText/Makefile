CC=$(SOPC_KIT_NIOS2)/bin/gnu/H-x86_64-pc-linux-gnu/bin/nios2-elf-gcc
OBJDUMP=$(SOPC_KIT_NIOS2)/bin/gnu/H-x86_64-pc-linux-gnu/bin/nios2-elf-objdump
ELF2HEX=$(SOPC_KIT_NIOS2)/bin/elf2hex

all: testVGAText.elf hex disasm

clean:
	rm -f *.elf
	rm -f *.hex
	rm -f *.disasm

hex: testVGAText.hex

disasm: testVGAText.disasm

testVGAText.elf: testVGAText.c
	$(CC) testVGAText.c -o testVGAText.elf -ffunction-sections -T testVGAText.ld -nostdlib
	


testVGAText.disasm: testVGAText.elf
	$(OBJDUMP) -d testVGAText.elf > testVGAText.disasm

testVGAText.hex: testVGAText.elf
	$(ELF2HEX) testVGAText.elf --width=8 --base=0x0 --end=0x300

