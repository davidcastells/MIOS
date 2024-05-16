#define LA (1<<0)
#define LB (1<<1)
#define LC (1<<2)
#define LD (1<<3)
#define LE (1<<4)
#define LF (1<<5)
#define LG (1<<6)

void testLED()
{
        int sa[8];
        int sb[8];
        int i = 0;

        sa[0] = LA;
        sa[1] = LB;
        sa[2] = LC;
        sa[3] = LD;
        sa[4] = sa[5] = sa[6] = sa[7] = 0;

        sb[0] = sb[1] = sb[2] = sb[3] = 0;
        sb[4] = LD;
        sb[5] = LE;
        sb[6] = LF;
        sb[7] = LA;

        while(1)
        {

        // we will do a sequence
        // n, a, b
                __builtin_custom_inii(0, sa[i], sb[i]);
                i = (i+1) % 8;
        }
}


void _start()
{
        testLED();
}
