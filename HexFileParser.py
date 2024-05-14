import intelhex

class HexFileParser:
    
    def loadMem(self, filename, memory, offset):
        data = intelhex.IntelHex(filename)
        
        for i in range(len(data)):
            memory.writeByte(offset+i, data[i])
            
        