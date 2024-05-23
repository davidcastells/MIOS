
#define BASE_VGA 0xB8000

#define FOREGROUND_BLACK   0
#define FOREGROUND_BLUE    1
#define FOREGROUND_GREEN   2
#define FOREGROUND_CYAN    3
#define FOREGROUND_RED     4
#define FOREGROUND_MAGENTA 5
#define FOREGROUND_BROWN   6
#define FOREGROUND_LIGHT_GRAY 7
#define FOREGROUND_DARK_GRAY  8
#define FOREGROUND_LIGHT_BLUE 9
#define FOREGROUND_LIGHT_GREEN 10
#define FOREGROUND_LIGHT_CYAN  11
#define FOREGROUND_LIGHT_RED   12
#define FOREGROUND_LIGHT_MAGENTA 13
#define FOREGROUND_YELLOW  14
#define FOREGROUND_WHITE   15

#define BACKGROUND_BLACK   0
#define BACKGROUND_RED     1
#define BACKGROUND_GREEN   2
#define BACKGROUND_BLUE    3
#define BACKGROUND_CYAN    4
#define BACKGROUND_MAGENTA 5
#define BACKGROUND_YELLOW  6
#define BACKGROUND_WHITE   7


#define IOWR_8DIRECT(base, offset, data) \
    (*(volatile unsigned char*)((base) + (offset)) = (data))

#define IOWR_32DIRECT(base, offset, data) \
    (*(volatile unsigned int *)((base) + (offset)) = (data))


#define NULL 0

void setChar(int x, int y, char c, int fg, int bg)
{
	IOWR_8DIRECT(BASE_VGA, y*80*2+x*2, c);
	IOWR_8DIRECT(BASE_VGA, y*80*2+x*2+1, bg << 4 | fg);
}


	
void testVGA()
{
        int i = 0;
        int fg = 0;
        int bg = 7;

        int x = 0;
        int y = 0;

        setChar(x++,y, 'H', FOREGROUND_BLACK, BACKGROUND_BLUE);
        setChar(x++,y, 'e', FOREGROUND_LIGHT_CYAN, BACKGROUND_RED);
        setChar(x++,y, 'l', FOREGROUND_LIGHT_MAGENTA, BACKGROUND_GREEN);
        setChar(x++,y, 'l', FOREGROUND_BLUE, BACKGROUND_YELLOW);
        setChar(x++,y, 'o', FOREGROUND_LIGHT_RED, BACKGROUND_CYAN);
        
        setChar(x++,y, '!', FOREGROUND_DARK_GRAY, BACKGROUND_MAGENTA);
                
        while (1);
}


void _start()
{
        testVGA();
}
