# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 17:00:44 2024

@author: dcr
"""

import Mios
import py4hw
from SevenSegmentsDisplay import *

import numpy as np

class Memory(py4hw.Logic):
    def __init__(self, parent, name, bus, size):
        super().__init__(parent, name)
        
        self.bus = self.addInterfaceSink('', bus)
        
        
        self.data = np.zeros(size//4, dtype=np.uint32)
        
    def writeByte(self, address, value):
        vadd = address // 4
        vbyte = address % 4
        mask = ~(0xff << vbyte*8) & 0xFFFFFFFF
        v = self.data[vadd]
        v = (v & mask) | ((value & 0xFF) << (vbyte * 8))
        
        #print(vadd, hex(v))
        self.data[vadd] = v
        
    def propagate(self ):
        address = self.bus.address.get()
        vadd = (address ) // 4
        vbyte = address % 4
        
        if (self.bus.read.get()==0 and self.bus.write.get() == 0):
            return
            
        if (vbyte != 0):
            raise Exception('Unaligned memory operation {:02X}'.format(vbyte))
            
        if (vadd > len(self.data)):
            raise Exception('Memory access {:08X} out of bounds'.format(address))

        self.bus.readdata.put(self.data[vadd])
        
        if (self.bus.write.get()):
            self.data[vadd] = self.bus.writedata.get() & 0xFFFFFFFF
        
    def on_button_click(self):
        pass
    
    
        
    def tkinter_gui(self, parent):
        from tkinter import ttk
        import tkinter as tk
        
        #print('parent',  type(parent))
        frame = ttk.Frame(parent, padding="10")
        #frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        #parent.add(frame)

        # Create Treeview with five columns
        columns = ("address", "3", "2", "1", "0")
        tree = ttk.Treeview(frame, columns=columns, show="headings")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)

        # Add headings to the columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)  # Adjust width as needed

        # Insert sample data into the treeview
        for i in range(len(self.data)):
            v = self.data[i]
            
            #print('value', i, '=', v)
            
            b0 = v & 0xFF
            v = v >> 8
            b1 = v & 0xFF
            v = v >> 8
            b2 = v & 0xFF
            v = v >> 8
            b3 = v & 0xFF
            
            tree.insert("", "end", values=("{:08X}".format(i*4), '{:02X}'.format(b3), '{:02X}'.format(b2), '{:02X}'.format(b1), '{:02X}'.format(b0)))

        # Create label, entry box, and button
        label = ttk.Label(frame, text="Selected Item:")
        edit_box = ttk.Entry(frame)
        button = ttk.Button(frame, text="Update", command=self.on_button_click)

        # Grid layout for Treeview
        tree.grid(column=0, row=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        vsb.grid(column=3, row=0,  sticky="ns")

        # Grid layout for label, entry box, and button
        label.grid(column=0, row=1, padx=10, pady=5, sticky="w")
        edit_box.grid(column=1, row=1, padx=10, pady=5, sticky="ew")
        button.grid(column=2, row=1, padx=10, pady=5, sticky="e")

        # Configure row and column weights for expanding
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        return frame


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
        
        



    
sys = py4hw.HWSystem()
        
cpuBus = Mios.AvalonMMInterface(sys, 'cpu_bus')
dataBus = Mios.AvalonMMInterface(sys, 'data_bus')
insBus = Mios.AvalonMMInterface(sys, 'ins_bus')
uartBus = Mios.AvalonMMInterface(sys, 'uart_bus')
perfBus = Mios.AvalonMMInterface(sys, 'perf_bus')

insMem = Memory(sys, 'ins_mem', insBus, 0x400 * 8)      # 8 kb instruction Memory
dataMem = Memory(sys, 'data_mem', dataBus, 0x400 * 8)   # 8 kb data Memory

# txd = sys.wire('txd')
# rxd = sys.wire('rxd')

# uart = AvalonUart(sys, 'uart', uartBus, txd, rxd, 50000000, 115200)

perf = PerformanceCounter(sys, 'perf', perfBus);


avalonDecoder = Mios.AvalonMMDecoder(sys, 'decoder', cpuBus, 
                              [insBus, perfBus, dataBus],
                              [0,  0x21040, 0x4000],
                              [0x400 * 8,  32, 0x400 * 8])

avalonMux = Mios.AvalonMMMux(sys, 'mux', cpuBus, 
                              [insBus, perfBus, dataBus],
                              [0,  0x21040, 0x4000],
                              [0x400 * 8,  32, 0x400 * 8])

ciBus = Mios.CustomInstructionInterface(sys, 'ci');
        

N1 = sys.wire('N1', 8);
N0 = sys.wire('N0', 8);

leds = SevenSegmentsDriver(sys, 'drv', ciBus, N1, N0)

SevenSegmentsDisplay(sys, 'N1', N1);
SevenSegmentsDisplay(sys, 'N0', N0);


niosii = Mios.Mios(sys, 'niosii', cpuBus, ciBus, 0x0 , 0, 0x4000 + 0x400 * 8)


import HexFileParser

hfp = HexFileParser.HexFileParser()
hfp.loadMem('software/testLEDCI/testLEDCI.hex', insMem, 0x0)

#setTestProgram()

py4hw.gui.Workbench(sys)

