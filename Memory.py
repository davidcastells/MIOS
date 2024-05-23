import py4hw
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
        
        
class SparseMemory(py4hw.Logic):
    def __init__(self, parent, name, bus, mem_base):
        super().__init__(parent, name)
        
        self.bus = self.addInterfaceSink('', bus)
        self.maxSize = (1 << bus.address.getWidth()) * (bus.writedata.getWidth() // 8)
        
        self.mem_base = mem_base # Memory Base is just informative, address decoding is centralized
        self.area = []
        self.verbose = False
        
    def getMaxSize(self):
        return self.maxSize
        
    def reallocArea(self, offset, size):
        start = offset
        end = offset + size -1
        mem_base = self.mem_base
        
        # first check if it is already included , and expand 
        for block in self.area:
            bstart = block[0]
            bend = block[0] + block[1] -1
            
            if (start >= bstart and start <= bend and end >= bstart and end <= bend):
                print('new block already included in {:016X}-{:016X}'.format(bstart+mem_base, bend+mem_base))
                return
            
            if (start >= bstart and start <= bend):
                print('new block start {:016X} included in {:016X}-{:016X}, updating start'.format(start+mem_base, bstart+mem_base, bend+mem_base))
                start = bstart
                
            if (end >= bstart and end <= bend):
                print('new block end {:016X} included in {:016X}-{:016X}, updating start'.format(end+mem_base, bstart+mem_base, bend+mem_base))
                end = bend
                
        newsize = end + 1 - start
        
        if (newsize > size):
            size = newsize
            print('updating size to {:X} bytes'.format(size))
        
        # create area
        newarea = bytearray(size)
        newlist = []
        
        for block in self.area:
            bstart = block[0]
            bend = block[0] + block[1] -1
            bdata = block[2]
            
            if (bstart >= start and bstart <= end and bend >= start and bend <= end):
                print('copying block {:016X}-{:016X} into new block {:016X}-{:016X}'.format(bstart+mem_base, bend+mem_base, start+mem_base, end+mem_base))
                for i in range(len(bdata)):
                    newarea[bstart-start+i] = bdata[i]
                    
            else:
                newlist.append(block)
                
        
        #first avoid checking overlaps
        newlist.append((start, size, newarea))
        print(f'sparse mem += 0x{start:X} - 0x{size:X}');
        
        self.area = newlist
        
    def writeByte(self, address, value):
        
        for area in self.area:
            offset = area[0]
            size = area[1]
            data = area[2]
            #print('mem write byte address:{} - range: [{},{}]'.format(address, offset, size) )

            if (address >= offset and address <= (offset+size)):
                data[address-offset] = value
                return

        raise Exception('Address {:0X} not in memory'.format(address + self.mem_base))
        
    def readByte(self, address):
        for area in self.area:
            offset = area[0]
            size = area[1]
            data = area[2]
            #print('mem write byte address:{} - range: [{},{}]'.format(address, offset, size) )

            if (address >= offset and address <= (offset+size)):
                return data[address-offset]                 

        raise Exception('Address {:0X} not in memory'.format(address + self.mem_base))
        
    def propagate(self ):
        data_width = self.bus.readdata.getWidth()
        
        address = self.bus.address.get()
        be = self.bus.be.get()

        
        if (self.bus.read.get()):

            value = 0
            
            # in little endian less significant byte is stored first
            # 0x0102 would be stored as 0x02 0x01
            for i in range(data_width // 8):                
                value = value | (self.readByte(address+i) << (i*8))
                
            self.bus.readdata.prepare(value)
            if (self.verbose): print('reading address ', hex(address+self.mem_base), '=', hex(value))

        elif (self.bus.write.get()):

            value = self.bus.writedata.get()

            if (self.verbose): print('writing address ', hex(address+self.mem_base), '=', hex(value))
            
            # in little endian less significant byte is stored first
            # 0x0102 would be stored as 0x02 0x01
            
            for i in range(data_width // 8):           
                if ((be & 0x1) != 0):
                    self.writeByte(address + i, value & 0xFF)
                be = be >> 1
                value = value >> 8
        
    
