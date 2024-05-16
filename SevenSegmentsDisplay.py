# -*- coding: utf-8 -*-
import py4hw

class SevenSegmentsDriver(py4hw.Logic):
    def __init__(self, parent, name, bus, N1, N0):
        super().__init__(parent, name)
        
        self.N1 = self.addOut('N1', N1)
        self.N0 = self.addOut('N0', N0)
        
        self.bus = self.addInterfaceSink('', bus)
        
    def clock(self):
        # Always ready
        self.bus.done.prepare(1)
        
        if (self.bus.start.get()):
            print('CI A:', self.bus.dataa.get(), 'B:', self.bus.datab.get())
            self.N1.prepare(self.bus.dataa.get())
            self.N0.prepare(self.bus.datab.get())
        
class SevenSegmentsDisplay(py4hw.Logic):
    def __init__(self, parent, name, seven):
        super().__init__(parent, name)
        
        self.seven = self.addIn('seven', seven)
        
    def tkinter_gui(self, parent):
        import tkinter as tk
        sl = 50
        sw = 5
        canvas = tk.Canvas(parent, width=sl+sw*4, height=sl*2+sw*4, bg="white")
        canvas.pack()

            # Draw the 7-segment display for the given digit
        self.draw_digit(canvas, self.seven.get(), sw*2, sw*2, sl, sw)

        return canvas


    def draw_segment(self, canvas, points):
        canvas.create_polygon(points, fill="red", outline="black")

    def draw_digit(self, canvas, v, x, y, sl, sw):
        # sl = segment length
        # sw = segment width
        
        # v = 0xff
        
        # Define segments for each digit (a-g)
        a = py4hw.BitManipulation.getBit(v, 0)
        b = py4hw.BitManipulation.getBit(v, 1)
        c = py4hw.BitManipulation.getBit(v, 2)
        d = py4hw.BitManipulation.getBit(v, 3)
        e = py4hw.BitManipulation.getBit(v, 4)
        f = py4hw.BitManipulation.getBit(v, 5)
        g = py4hw.BitManipulation.getBit(v, 6)
        
        
        segments = [
            [(0, 0), (sw, -sw), (sl-sw, -sw), (sl, 0), (sl-sw, sw), (sw, sw)],                              # a
            [(sl, 0), (sl+sw, sw), (sl+sw, sl-sw), (sl, sl), (sl-sw, sl-sw), (sl-sw, sw)],                  # b
            [(sl, sl), (sl+sw, sl+sw), (sl+sw, sl+sl-sw), (sl, sl+sl), (sl-sw, sl+sl-sw), (sl-sw, sl+sw)],  # c
            [(0, sl+sl), (sw, sl+sl-sw), (sl-sw, sl+sl-sw), (sl, sl+sl), (sl-sw, sl+sl+sw), (sw, sl+sl+sw)],                  # d
            [(0, sl), (sw, sl+sw), (sw, sl+sl-sw), (0, sl+sl), (-sw, sl+sl-sw), (-sw, sl+sw)],              # e
            [(0, 0), (sw, sw), (sw, sl-sw), (0, sl), (-sw, sl-sw), (-sw, sw)],                              # f
            [(0, sl), (sw, sl-sw), (sl-sw, sl-sw), (sl, sl), (sl-sw, sl+sw), (sw, sl+sw)],                  # g
        ]
    
        digit_segments = [a,b,c,d,e,f,g]
    
        # Draw segments based on the digit
        for i in range(len(digit_segments)):
            if (digit_segments[i]):
                segment = segments[i]
                points = [(x + point[0], y + point[1]) for point in segment]
                self.draw_segment(canvas, points)
                
                
class SevenSegmentsSlaveDevice(py4hw.Logic):
    def __init__(self, parent, name, bus):
        super().__init__(parent, name)
        
        self.bus = self.addInterfaceSink('', bus)
        self.N0 = 0
        self.N1 = 0
        
        
    def clock(self):
        if (self.bus.write.get()):
            print('writing LEDs')
            self.N0 = self.bus.writedata.get() & 0xFF
            self.N1 = (self.bus.writedata.get() >> 8) & 0xFF
            
    def tkinter_gui(self, parent):
        import tkinter as tk
        sl = 50
        sw = 5
        canvas = tk.Canvas(parent, width=sl+sw*10, height=sl*2+sw*4, bg="white")
        canvas.pack()

            # Draw the 7-segment display for the given digit
        self.draw_digit(canvas, self.N0, sw*2 + sw*15, sw*2, sl, sw)
        self.draw_digit(canvas, self.N1, sw*2, sw*2, sl, sw)

        return canvas
    
    def draw_segment(self, canvas, points, fill=True):
        if (fill):
            canvas.create_polygon(points, fill="red", outline="black")
        else:
            canvas.create_polygon(points, fill="white", outline="lightgray")
        
    def draw_digit(self, canvas, v, x, y, sl, sw):
        # sl = segment length
        # sw = segment width
        
        # v = 0xff
        
        # Define segments for each digit (a-g)
        a = py4hw.BitManipulation.getBit(v, 0)
        b = py4hw.BitManipulation.getBit(v, 1)
        c = py4hw.BitManipulation.getBit(v, 2)
        d = py4hw.BitManipulation.getBit(v, 3)
        e = py4hw.BitManipulation.getBit(v, 4)
        f = py4hw.BitManipulation.getBit(v, 5)
        g = py4hw.BitManipulation.getBit(v, 6)
        
        
        segments = [
            [(0, 0), (sw, -sw), (sl-sw, -sw), (sl, 0), (sl-sw, sw), (sw, sw)],                              # a
            [(sl, 0), (sl+sw, sw), (sl+sw, sl-sw), (sl, sl), (sl-sw, sl-sw), (sl-sw, sw)],                  # b
            [(sl, sl), (sl+sw, sl+sw), (sl+sw, sl+sl-sw), (sl, sl+sl), (sl-sw, sl+sl-sw), (sl-sw, sl+sw)],  # c
            [(0, sl+sl), (sw, sl+sl-sw), (sl-sw, sl+sl-sw), (sl, sl+sl), (sl-sw, sl+sl+sw), (sw, sl+sl+sw)],                  # d
            [(0, sl), (sw, sl+sw), (sw, sl+sl-sw), (0, sl+sl), (-sw, sl+sl-sw), (-sw, sl+sw)],              # e
            [(0, 0), (sw, sw), (sw, sl-sw), (0, sl), (-sw, sl-sw), (-sw, sw)],                              # f
            [(0, sl), (sw, sl-sw), (sl-sw, sl-sw), (sl, sl), (sl-sw, sl+sw), (sw, sl+sw)],                  # g
        ]
    
        digit_segments = [a,b,c,d,e,f,g]

        # Draw outlines
        for i in range(len(digit_segments)):
            segment = segments[i]
            points = [(x + point[0], y + point[1]) for point in segment]
            self.draw_segment(canvas, points, False)
                
        # Draw segments based on the digit
        for i in range(len(digit_segments)):
            if (digit_segments[i]):
                segment = segments[i]
                points = [(x + point[0], y + point[1]) for point in segment]
                self.draw_segment(canvas, points)