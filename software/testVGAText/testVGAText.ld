ENTRY(_start)

SECTIONS {
    . = 0x0;

    .text._start :
    {
        *(.text._start)
    }

/* Define the _gp symbol */
    _gp = ALIGN(4);
    . = ALIGN(4);
    PROVIDE(_gp = .);

}

