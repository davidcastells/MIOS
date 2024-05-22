# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 15:20:49 2024

@author: dcr

  Check info from https://www-ug.eecg.toronto.edu/msl/manuals/n2cpu_nii51017.pdf

"""

import py4hw


class AvalonMMInterface(py4hw.Interface):
    def __init__(self, parent, name:str):
        super().__init__(parent, name)
        
        self.address = self.addSourceToSink('address', 32)
        self.write = self.addSourceToSink('write', 1)
        self.read = self.addSourceToSink('read', 1)
        self.writedata = self.addSourceToSink('writedata', 32)
        self.readdata = self.addSinkToSource('readdata', 32)
        self.be = self.addSourceToSink('be', 4)


class CustomInstructionInterface(py4hw.Interface):
    def __init__(self, parent, name:str):
        super().__init__(parent, name)
        
        self.en = self.addSourceToSink('en', 1)
        self.start = self.addSourceToSink('start', 1)
        self.n = self.addSourceToSink('n', 8)
        self.dataa = self.addSourceToSink('dataa', 32)
        self.datab = self.addSourceToSink('datab', 32)
        self.done = self.addSourceToSink('done', 1)
        self.r = self.addSourceToSink('r', 32)

class AvalonMMDecoder(py4hw.Logic):
    def __init__(self, parent, name, master, slaves, bases, sizes):
        super().__init__(parent, name)
        
        self.master = master 
        
        self.addIn('m0_address', master.address) 
        self.addIn('m0_write', master.write) 
        self.addIn('m0_read', master.read) 
        self.addIn('m0_writedata', master.writedata) 
        
        self.slaves = []
        self.bases = bases
        self.sizes = sizes
        
        for idx, slave in enumerate(slaves):
            #self.slaves.append(self.addInterfaceSource('s{}'.format(idx), slave))
            self.slaves.append(slave)
            name = 's{}'.format(idx)
            self.addOut(name+'_address', slave.address)
            self.addOut(name+'_write', slave.write)
            self.addOut(name+'_read', slave.read)
            self.addOut(name+'_writedata', slave.writedata)
        
    def propagate(self):
        add = self.master.address.get()
        
        for idx, slave in enumerate(self.slaves):
            
            
            if (add >= self.bases[idx] and add < (self.bases[idx]+self.sizes[idx])):
                self.slaves[idx].address.put(add - self.bases[idx])
                self.slaves[idx].write.put(self.master.write.get())    
                self.slaves[idx].read.put(self.master.read.get())    
                self.slaves[idx].writedata.put(self.master.writedata.get())    
                #self.master.readdata.put(self.slaves[idx].readdata.get())
            else:
                self.slaves[idx].address.put(0)
                self.slaves[idx].write.put(0)    
                self.slaves[idx].read.put(0)    
                self.slaves[idx].writedata.put(0)    
                
class AvalonMMMux(py4hw.Logic):
    def __init__(self, parent, name, master, slaves, bases, sizes):
        super().__init__(parent, name)
        
        self.master = master 
        
        self.addIn('m0_address', master.address) 
        self.addOut('m0_readdata', master.readdata) 
        
        self.slaves = []
        self.bases = bases
        self.sizes = sizes
        
        for idx, slave in enumerate(slaves):
            self.slaves.append(slave)
            name = 's{}'.format(idx)
            self.addIn(name+'_readdata', slave.readdata)
        
    def propagate(self):
        add = self.master.address.get()
        
        #print('Mux: add:', hex(add))
        
        for idx, slave in enumerate(self.slaves):
            
            if (add >= self.bases[idx] and add < (self.bases[idx]+self.sizes[idx])):
                #print('slave', idx, 'active: ', hex(self.slaves[idx].readdata.get()))
                self.master.readdata.put(self.slaves[idx].readdata.get())
            else:
                pass
    
class Mios(py4hw.Logic):
    '''
    This is a processor compatible with Altera NIOS2 ISA
    '''
    def __init__(self, parent, name, cpuBus, ciBus, startAddress, exceptionAddress, stackPointer=0):
        super().__init__(parent, name)
        
        
        
        self.cpuBus = self.addInterfaceSource('', cpuBus)
        
        if not(ciBus is None):
            self.ciBus = self.addInterfaceSource('', ciBus)
        else:
            self.ciBus = None
        
        self.pc = startAddress
        self.reg = [0] * 32
        self.reg[27] = stackPointer
        
        self.ctl = [0] * 32 # Control Registers
        
        self.reset_address = startAddress
        self.exception_address = exceptionAddress
        
        self.vaddress = 0
        self.vread = 0
        self.vwrite = 0
        self.vwritedata = 0
        self.vbe = 0
        self.vreaddata = 0
        
        self.vdataa = 0 
        self.vdatab = 0 
        self.vstart = 0
        self.vn = 0
        
        # Variables for the GUI
        self.pc_value = None
        self.ins_value = None
        
        
        self.co = self.run()
        
        
    def clock(self):
        # obtain values gets
        self.vreaddata = self.cpuBus.readdata.get()
        
        if not(self.ciBus is None):
            self.vdone = self.ciBus.done.get()
            self.vr = self.ciBus.r.get()
        
        next(self.co)
        
        # prepare values
        self.cpuBus.address.prepare(self.vaddress)    
        self.cpuBus.read.prepare(self.vread)    
        self.cpuBus.write.prepare(self.vwrite)    
        self.cpuBus.writedata.prepare(self.vwritedata)    
        self.cpuBus.be.prepare(self.vbe)    
        
        if not(self.ciBus is None):
            self.ciBus.dataa.prepare(self.vdataa)
            self.ciBus.datab.prepare(self.vdatab)
            self.ciBus.n.prepare(self.vn)
            self.ciBus.start.prepare(self.vstart)
        
        
    def bitr(self, v, high, low):
        r = (high-low) +1
        mask = (1 << r) -1
        return (v >> low) & mask
    
    def fetchIns(self):
        self.vaddress = self.pc
        self.vread = 1
        self.vwrite = 0
        self.vbe = 0xF
        
        yield
        yield
        self.ins = self.vreaddata
        self.vread = 0

    def storeByte(self, address, value):
        self.vaddress = address & 0xFFFFFFFC
        self.vread = 0
        self.vwrite = 1
        bit = (address & 0x3)
        self.vwritedata = (value & 0xFF) << bit
        self.vbe = 1 << bit
        yield
        self.vwrite = 0
                
    def storeWord(self, address, value):
        assert(address % 4 == 0)
        self.vaddress = address
        self.vread = 0
        self.vwrite = 1
        self.vwritedata = value
        self.vbe = 0xF
        yield
        self.vwrite = 0

    def loadByte(self, address):
        self.vaddress = address & 0xFFFFFFFC
        self.vread = 1
        self.vwrite = 0
        bit = (address & 0x3)
        yield
        self.vread = 0
        return (self.vreaddata >> bit) & 0xFF

        
    def loadWord(self, address):
        assert(address % 4 == 0)
        self.vaddress = address
        self.vread = 1
        self.vwrite = 0
        yield
        self.vread = 0
        return self.vreaddata
        
    def custom(self, ra, rb, rc, usea, useb, writec, n):
        
        print('custom')
        self.vstart = 1
        self.vdataa = self.reg[ra]
        self.vdatab = self.reg[rb]
        self.vn = n
        
        print('start', self.vstart, self.vdataa , self.vdatab)
        
        yield
        self.vstart = 0
        while (self.vdone == 0):
            yield
        
        if (writec):
            self.reg[rc] = self.vr
        
    def execute(self):
        v = self.ins
        op6 = self.bitr(v, 5, 0)
        
        # I type
        ra = self.bitr(v, 31, 27) 
        rb = self.bitr(v, 26, 22)
        imm16 = self.bitr(v, 21, 6)
        simm16 = (imm16 & 0x7FFF) - (imm16 & 0x8000)

        # R type
        rc = self.bitr(v, 21, 17) 
        opx = self.bitr(v, 16, 11)
        imm5 = self.bitr(v, 10, 6)
        
        # J Type
        imm26 = self.bitr(v, 31, 6) 
        
        if (op6 == 0x00):
            # call
            self.reg[31] = self.pc + 4
            self.pc = (self.pc & 0xF0000000) + imm26 * 4
            yield
            return
        
        if (op6 == 0x03):
            # ldbu
            self.reg[rb] = yield from self.loadByte(self.reg[ra] + simm16)
            
        elif (op6 == 0x04):
            # addi
            self.reg[rb] = (self.reg[ra] + simm16) & 0xFFFFFFFF
            
        elif (op6 == 0x05):
            # stb
            yield from self.storeByte(self.reg[ra] + simm16, self.reg[rb])
            
        elif (op6 == 0x06):
            # br
            self.pc = self.pc + 4 + simm16
            yield
            return
        
        elif (op6 == 0x0C):
            # andi
            self.reg[rb] = self.reg[ra] & imm16
            
        elif (op6 == 0x0e):
            # bge
            if (py4hw.IntegerHelper.c2_to_signed(self.reg[ra], 32) >= py4hw.IntegerHelper.c2_to_signed(self.reg[rb], 32)):
                self.pc = self.pc + 4 + simm16
                yield
                return
            
        elif (op6 == 0x14):
            # ori
            self.reg[rb] = self.reg[ra] | imm16
            
        elif (op6 == 0x15):
            # stw
            yield from self.storeWord(self.reg[ra] + simm16, self.reg[rb])
        elif (op6 == 0x16):
            # blt
            if (py4hw.IntegerHelper.c2_to_signed(self.reg[ra], 32) < py4hw.IntegerHelper.c2_to_signed(self.reg[rb], 32)):
                self.pc = self.pc + 4 + simm16
                yield
                return
                
        elif (op6 == 0x17):
            # ldw
            self.reg[rb] = yield from self.loadWord(self.reg[ra] + simm16)
            
        elif (op6 == 0x1E):
            # bne
            if (self.reg[ra] != self.reg[rb]):
                self.pc = self.pc + 4 + simm16
                yield
                return
                

        elif (op6 == 0x26):
            # beq
            if (self.reg[ra] == self.reg[rb]):
                self.pc = self.pc + 4 + simm16
                yield
                return
        elif (op6 == 0x28):
            # cmpgeui
            self.reg[rb] = 1 if (self.reg[ra] >= imm16) else 0
            
        elif (op6 == 0x2C):
            # andhi
            self.reg[rb] = self.reg[ra] & (imm16 << 16)
            
        elif (op6 == 0x32):
            # custom
            usea = self.bitr(v, 16, 16)
            useb = self.bitr(v, 15, 15)
            writec = self.bitr(v, 14, 14)
            n = self.bitr(v, 13, 6)
            yield from self.custom(ra, rb, rc, usea, useb, writec, n)
            
        elif (op6 == 0x33):
            # initd
            pass
            
        elif (op6 == 0x34):
            # orhi
            self.reg[rb] = self.reg[ra] | (imm16 << 16)
            
        elif (op6 == 0x3A):
            if (opx == 0x05):
                # ret
                self.pc = self.reg[31]
                yield
                return
                
            elif (opx == 0x0e):
                # and
                self.reg[rc] = self.reg[ra] & self.reg[rb]
                
            elif (opx == 0x12):
                # slli
                self.reg[rc] = self.reg[ra] << imm5
                
            elif (opx == 0x16):
                # or
                self.reg[rc] = self.reg[ra] | self.reg[rb]
                
            elif (opx == 0x1A):
                # srli
                self.reg[rc] = self.reg[ra] >> imm5

            elif (opx == 0x1C):
                # nextpc
                self.reg[rc] = self.pc + 4
                
            elif (opx == 0x1D):
                # callr
                self.reg[31] = self.pc + 4
                self.pc = self.reg[ra]
                yield
                return
                
            elif (opx == 0x20):
                # cmpeq
                if (self.reg[ra] == self.reg[rb]):
                    self.reg[rc] == 1
                else:
                    self.reg[rc] == 0
            elif (opx == 0x29):
                # initi
                pass
            elif (opx == 0x2E):
                # wrctl
                self.ctl[imm5] = self.reg[ra]
               
            elif (opx == 0x31):
                # add
                self.reg[rc] = self.reg[ra] + self.reg[rb]
            elif (opx == 0x39):
                # sub
                self.reg[rc] = (self.reg[ra] - self.reg[rb]) & 0xFFFFFFFF
            else:
                print('op=', hex(op6), 'opx=', hex(opx))
                
                
        elif (op6 == 0x3B):
            # flushd
            pass
        else:
            print('op=', hex(op6), 'opx=', hex(opx))
        
        self.pc += 4
        
        yield
        
    def run(self):
        from Disassembler import Disassembler
        while (True):
            yield from self.fetchIns()
            print('{:04X}: 0x{:08X}'.format(self.pc, self.ins), Disassembler.disasm(self.ins))
            
            if not(self.pc_value is None):
                self.pc_value.set('{:04X}'.format(self.pc))
                self.ins_value.set(Disassembler.disasm(self.ins))
            
            yield from self.execute()
            
            
    def tkinter_gui(self, parent):
        from tkinter import ttk
        import tkinter as tk
        
        # print('parent',  type(parent))
        frame = ttk.Frame(parent, padding="10")
        #frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create Treeview with five columns
        columns = ("register", "value" )
        tree = ttk.Treeview(frame, columns=columns, show="headings")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)

        # Add headings to the columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)  # Adjust width as needed

        # Insert sample data into the treeview
        for i in range(32):
            v = self.reg[i]
            
            tree.insert("", "end", values=(i, "{:08X}".format(v)) )

        # Create label and read-only entry box for PC
        if (self.pc_value is None):
            self.pc_value = tk.StringVar()
            self.ins_value = tk.StringVar()
        
        pc_label = ttk.Label(frame, text="PC")
        pc_entry = ttk.Entry(frame, textvariable=self.pc_value) # state="readonly"
        
        ins_label = ttk.Label(frame, text='Instruction')
        ins_entry = ttk.Entry(frame, textvariable=self.ins_value)
    
        # Create label, entry box, and button
        #label = ttk.Label(frame, text="Selected Item:")
        #edit_box = ttk.Entry(frame)
        #button = ttk.Button(frame, text="Update", command=self.on_button_click)

        # Grid layout for Treeview
        tree.grid(column=0, columnspan=2, row=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        #vsb.grid(column=3, row=0,  sticky="ns")

        # Grid layout for label and entry box
        pc_label.grid(column=0, row=1, padx=10, pady=5, sticky="w")
        pc_entry.grid(column=1, row=1, padx=10, pady=5, sticky="w")
        
        ins_label.grid(column=0, row=2, padx=10, pady=5, sticky="w")
        ins_entry.grid(column=1, row=2, padx=10, pady=5, sticky="w")

        # Grid layout for label, entry box, and button
        #label.grid(column=0, row=1, padx=10, pady=5, sticky="w")
        #edit_box.grid(column=1, row=1, padx=10, pady=5, sticky="ew")
        #button.grid(column=2, row=1, padx=10, pady=5, sticky="e")

        # Configure row and column weights for expanding
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        return frame
