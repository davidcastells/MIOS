ENTRY(_start)

SECTIONS {
    . = 0x0;

    .text._start :
    {
        *(.text._start)
    }


}

