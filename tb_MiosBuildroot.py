# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 17:00:44 2024

@author: dcr
"""

import py4hw
from SevenSegmentsDisplay import *
from Memory import *
import Mios

import numpy as np
import math

def loadElf(filename, memory,  offset):
    from elftools.elf.elffile import ELFFile

    f = open(filename,'rb')
    elffile = ELFFile(f,'rb')

    for seg in elffile.iter_segments():
        if seg['p_type'] == 'PT_LOAD':
            adr = seg['p_paddr']
            data = seg.data()
            size = len(data)
            print('ELF segment. address: {:016X} - {:016X}'.format(adr, adr+size))
            
            memory.reallocArea(adr - offset, 1 << int(math.ceil(math.log2(size))))
            p = adr - offset
            for x in data:
                memory.writeByte(p, x)
                p += 1
                



class AvalonUart(py4hw.Logic):
    def __init__(self, parent, name, bus, txd, rxd, sysfreq, baud):
        super().__init__(parent, name)
        
        self.addInterfaceSink('', bus)
        
        self.txd = self.addOut('txd', txd)
        self.rxd = self.addIn('rxd', rxd)

class PerformanceCounter(py4hw.Logic):
    def __init__(self, parent, name, bus):
        super().__init__(parent, name)
        
        self.addInterfaceSink('', bus)
        
        
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


    
hw = py4hw.HWSystem()
        
cpuBus = Mios.AvalonMMInterface(hw, 'cpu_bus')
dataBus = Mios.AvalonMMInterface(hw, 'data_bus')
insBus = Mios.AvalonMMInterface(hw, 'ins_bus')
uartBus = Mios.AvalonMMInterface(hw, 'uart_bus')
perfBus = Mios.AvalonMMInterface(hw, 'perf_bus')
sevBus = Mios.AvalonMMInterface(hw, 'sev_bus')

mem_base = 0xC8000000
mem_size = 0x08000000

insMem = Memory(hw, 'ins_mem', insBus, 0x400 )      # 1 kb  Memory
dataMem = SparseMemory(hw, 'data_mem', dataBus, mem_base)   # 128 MB data Memory

#dataMem.reallocArea(0, mem_size)

# txd = sys.wire('txd')
# rxd = sys.wire('rxd')

# uart = AvalonUart(sys, 'uart', uartBus, txd, rxd, 50000000, 115200)

perf = PerformanceCounter(hw, 'perf', perfBus)
sev = SevenSegmentsSlaveDevice(hw, 'sev', sevBus)


avalonDecoder = Mios.AvalonMMDecoder(hw, 'decoder', cpuBus, 
                              [insBus, perfBus, dataBus, sevBus],
                              [0,  0x21040, mem_base, 0x21200],
                              [0x400 ,  32, mem_size, 32])

avalonMux = Mios.AvalonMMMux(hw, 'mux', cpuBus, 
                              [insBus, perfBus, dataBus, sevBus],
                              [0,  0x21040, mem_base, 0x21200],
                              [0x400 ,  32, mem_size, 32])

#ciBus = Mios.CustomInstructionInterface(sys, 'ci');
        

#N1 = sys.wire('N1', 8);
#N0 = sys.wire('N0', 8);

#leds = SevenSegmentsDriver(sys, 'drv', ciBus, N1, N0)

#SevenSegmentsDisplay(sys, 'N1', N1);
#SevenSegmentsDisplay(sys, 'N0', N0);


niosii = Mios.Mios(hw, 'niosii', cpuBus, None, 0xc8000000 , 0xc8000120 )


import HexFileParser

# hfp = HexFileParser.HexFileParser()
loadElf('software/buildroot/vmlinux', dataMem, mem_base)

#setTestProgram()

tbreak_address = None

def tbreak(add):
    global tbreak_address
    tbreak_address = add
    
def go():
    import time
    global tbreak_address
    sim = hw.getSimulator()
    sim.do_run = True
    count = 0
    
    cpu = niosii
    
    t0 = time.time()
    clk0 = sim.total_clks
    
    while (cpu.pc != tbreak_address and sim.do_run == True ):
        inipc = cpu.pc
        while (cpu.pc == inipc and sim.do_run == True ):
            sim.clk(1)
            
        count += 1            

    tf = time.time()
    clkf = sim.total_clks
    
    if (tf != t0):    
        freq = (clkf-clk0)/(tf-t0)
    else:
        freq = '?'
        
    print('clks: {} time: {} simulation freq: {}'.format(clkf-clk0, tf-t0, freq))
    tbreak_address = None
        
def step(steps = 1):
    sim = hw.getSimulator()
    sim.do_run = True
    count = 0
    cpu = niosii
    
    while (count < steps and sim.do_run == True ):
        inipc = cpu.pc
        while (cpu.pc == inipc and sim.do_run == True ):
            sim.clk(1)
            
        count += 1

def regs():
    cpu = niosii
    print('pc: {:016X}'.format(cpu.pc))
    for i in range(8):
        print('r{:2}={:016X}  |  r{:2}={:016X}  |  r{:2}={:016X}  |  r{:2}={:016X} '.format(
            i, cpu.reg[i], i+8, cpu.reg[i+8], i+16, cpu.reg[i+16], i+24, cpu.reg[i+24]))
           
def ctl_regs():    
    cpu = niosii        
    for i in range(8):
        print('ctl{:2}={:016X}  |  ctl{:2}={:016X}  |  ctl{:2}={:016X}  |  ctl{:2}={:016X} '.format(
            i, cpu.ctl[i], i+8, cpu.ctl[i+8], i+16, cpu.ctl[i+16], i+24, cpu.ctl[i+24]))
#py4hw.gui.Workbench(sys)

