# -*- coding: utf-8 -*-
import py4hw

import numpy as np
                
                
class VGAText(py4hw.Logic):
    def __init__(self, parent, name, bus):
        super().__init__(parent, name)
        
        self.bus = self.addInterfaceSink('', bus)
        
        self.data = np.zeros(25*80*2, dtype=int)

        
    def clock(self):
        if (self.bus.write.get()):

            add = self.bus.address.get()
            be = self.bus.be.get()
            v = self.bus.writedata.get()

            #print(f'write VGA {add:X} be:{be:X} = {v:X}')
            
                        
            if (be == 0x01):   
                v = v & 0xFF
            elif (be == 0x02): 
                v = (v >> 8) & 0xFF
                add += 1
            elif (be == 0x04): 
                v = (v >> 16) & 0xFF
                add += 2
            elif (be == 0x08): 
                v = (v >> 24) & 0xFF
                add += 3
                
            print(f'write VGA {add:X} = {v:X}')

            self.data[add] = v
            

            
    def draw_text(self, canvas, text, x, y, fg, bg, bw, bh, font=('Courier', 15)):
        # Measure the text size to fit the background rectangle
        text_id = canvas.create_text(x, y, text=text, fill=fg, font=font, anchor='nw')
        rect_id = canvas.create_rectangle(x, y, x + bw, y + bh, fill=bg, outline='')
    
        
        canvas.tag_raise(text_id, rect_id)
    
    def extractcolor(self, color):
        fg = color & 0xF
        bg = (color >> 4) & 0x7

        fg_map = {0:"black", 1: "blue", 2: "green", 3: "cyan", 4: "red", 5: "magenta",6: "brown", 7: "#AAAAAA", 
                  8: "#555555", 9: "#5555FF", 10: "#55FF55", 11: "#55FFFF",  12: "#FF5555", 13: "#FF55FF", 14: "yellow", 15: "white" }
        bg_map = {0:"black", 1: "red", 2: "green", 3: "blue", 4: "cyan", 5: "magenta",6: "yellow", 7: "white"}
        
        return fg_map[fg], bg_map[bg]
      

    def tkinter_gui(self, parent):
        import tkinter as tk
        sl = 20
        sw = 20
        canvas = tk.Canvas(parent, width=sw*10, height=sl*2+sw*4, bg="white")
        canvas.pack()

        for r in range(25):
            for c in range(80):
                ascii = self.data[r*80*2+c*2]
                color = self.data[r*80*2+c*2+1]
                fg, bg = self.extractcolor(color)
                
                self.draw_text(canvas, chr(ascii), c*sw, r*sl, fg, bg, sw, sl) 

        return canvas
    

