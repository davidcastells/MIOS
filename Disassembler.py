# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 19:17:19 2024

@author: dcr
"""

#  Check info from https://www-ug.eecg.toronto.edu/msl/manuals/n2cpu_nii51017.pdf


class Disassembler:
    
    @staticmethod
    def bitr(v, high, low):
        r = (high-low) +1
        mask = (1 << r) -1
        return (v >> low) & mask
        
    @staticmethod
    def disasm(v):
        op6 = Disassembler.bitr(v, 5, 0)
        
        # I type
        ra = Disassembler.bitr(v, 31, 27) 
        rb = Disassembler.bitr(v, 26, 22)
        imm16 = Disassembler.bitr(v, 21, 6)
        simm16 = (imm16 & 0x7FFF) - (imm16 & 0x8000)

        # R type
        rc = Disassembler.bitr(v, 21, 17) 
        opx = Disassembler.bitr(v, 16, 11)
        imm5 = Disassembler.bitr(v, 10, 6)
        
        # J Type
        imm26 = Disassembler.bitr(v, 31, 6) 
        
        # Custom
        n = Disassembler.bitr(v, 13, 6)
        
        sop_table = {0x00:'call', 0x01: 'jmpi', 0x02: '',  0x03: 'lbdu', 0x04:'addi', 0x05:'stb', 0x06:'br', 0x07:'ldb', 
                     0x08:'cmpgei', 0x09:'', 0x0A:'', 0x0B:'ldhu', 0x0C:'andi', 0x0D:'sth', 0x0E:'bge', 0x0F:'ldh',
                     0x10:'cmplti', 0x11:'', 0x12:'', 0x13:'initda', 0x14:'ori', 0x15:'stw', 0x16:'blt', 0x17:'ldw', 
                     0x18:'cmpnei', 0x19:'', 0x1A:'', 0x1B:'flushda', 0x1C:'xori', 0x1D:'', 0x1E:'bne', 0x1F:'',
                     0x20:'cmpeqi', 0x21:'', 0x22:'', 0x23:'ldbuio', 0x24:'muli', 0x25:'stbio', 0x26:'beq', 0x27:'ldbio',
                     0x28:'cmpgeui', 0x29:'', 0x2A:'', 0x2B:'ldhuio', 0x2C:'andhi', 0x2D:'sthio', 0x2E:'bgeu', 0x2F:'ldhio',
                     0x30:'cmpltui', 0x31:'', 0x32:'custom', 0x33:'initd', 0x34:'orhi', 0x35:'stwio', 0x36:'bltu', 0x37:'ldwio',
                     0x38:'', 0x39:'', 0x3A:'', 0x3B:'flushd', 0x3C:'xorhi', 0x3D:'', 0x3E:'', 0x3F:''}
        
        
        sopx_table = {0x00:'', 0x01: 'eret', 0x02: 'roli',  0x03: 'rol', 0x04:'flushp', 0x05:'ret', 0x06:'nor', 0x07:'mulxuu', 
                     0x08:'cmpge', 0x09:'bret', 0x0A:'', 0x0B:'ror', 0x0C:'flushi', 0x0D:'jmp', 0x0E:'and', 0x0F:'',
                     0x10:'cmplt', 0x11:'', 0x12:'slli', 0x13:'sll', 0x14:'', 0x15:'', 0x16:'or', 0x17:'mulxsu', 
                     0x18:'cmpne', 0x19:'', 0x1A:'srli', 0x1B:'srl', 0x1C:'nextpc', 0x1D:'callr', 0x1E:'xor', 0x1F:'mulxss',
                     0x20:'cmpeq', 0x21:'', 0x22:'', 0x23:'', 0x24:'divu', 0x25:'div', 0x26:'rdctl', 0x27:'mul',
                     0x28:'cmpgeu', 0x29:'initi', 0x2A:'', 0x2B:'', 0x2C:'', 0x2D:'trap', 0x2E:'wrctl', 0x2F:'',
                     0x30:'cmpltu', 0x31:'add', 0x32:'', 0x33:'', 0x34:'break', 0x35:'', 0x36:'sync', 0x37:'',
                     0x38:'', 0x39:'sub', 0x3A:'srai', 0x3B:'sra', 0x3C:'', 0x3D:'', 0x3E:'', 0x3F:''}

        stype_table = {0x0:'J', 0x01: 'jmpi', 0x02: '',  0x03: 'lbdu', 0x04:'IS', 0x05:'stb', 0x06:'BR', 0x07:'ldb',
                       0x08:'cmpgei', 0x09:'', 0x0A:'', 0x0B:'ldhu', 0x0C:'I', 0x0D:'sth', 0x0E:'I', 0x0F:'ldh',
                       0x10:'cmplti', 0x11:'', 0x12:'', 0x13:'initda', 0x14:'ori', 0x15:'SBO', 0x16:'blt', 0x17:'LBO', 
                       0x18:'cmpnei', 0x19:'', 0x1A:'', 0x1B:'flushda', 0x1C:'xori', 0x1D:'', 0x1E:'bne', 0x1F:'',
                       0x20:'cmpeqi', 0x21:'', 0x22:'', 0x23:'ldbuio', 0x24:'muli', 0x25:'stbio', 0x26:'beq', 0x27:'ldbio',
                       0x28:'cmpgeui', 0x29:'', 0x2A:'', 0x2B:'ldhuio', 0x2C:'andhi', 0x2D:'sthio', 0x2E:'bgeu', 0x2F:'ldhio',
                       0x30:'cmpltui', 0x31:'', 0x32:'CU', 0x33:'initd', 0x34:'I', 0x35:'stwio', 0x36:'bltu', 0x37:'ldwio',
                       0x38:'', 0x39:'', 0x3A:'', 0x3B:'flushd', 0x3C:'xorhi', 0x3D:'', 0x3E:'', 0x3F:''}
        
        stypex_table = {0x00:'', 0x01: 'eret', 0x02: 'RI',  0x03: 'rol', 0x04:'flushp', 0x05:'ret', 0x06:'nor', 0x07:'mulxuu', 
                     0x08:'cmpge', 0x09:'bret', 0x0A:'', 0x0B:'ror', 0x0C:'flushi', 0x0D:'jmp', 0x0E:'R', 0x0F:'',
                     0x10:'cmplt', 0x11:'', 0x12:'RI', 0x13:'sll', 0x14:'', 0x15:'', 0x16:'or', 0x17:'mulxsu', 
                     0x18:'cmpne', 0x19:'', 0x1A:'srli', 0x1B:'srl', 0x1C:'nextpc', 0x1D:'callr', 0x1E:'xor', 0x1F:'mulxss',
                     0x20:'R', 0x21:'', 0x22:'', 0x23:'', 0x24:'divu', 0x25:'div', 0x26:'rdctl', 0x27:'mul',
                     0x28:'cmpgeu', 0x29:'initi', 0x2A:'', 0x2B:'', 0x2C:'', 0x2D:'trap', 0x2E:'wrctl', 0x2F:'',
                     0x30:'cmpltu', 0x31:'R', 0x32:'', 0x33:'', 0x34:'break', 0x35:'', 0x36:'sync', 0x37:'',
                     0x38:'', 0x39:'sub', 0x3A:'srai', 0x3B:'sra', 0x3C:'', 0x3D:'', 0x3E:'', 0x3F:''}
        
        sop = sop_table[op6]
        stype = stype_table[op6]
        
        if (op6 == 0x3A):
            sop = sopx_table[opx]
            stype = stypex_table[opx]
        
        if (stype == 'I'):
            return '{} r{}, r{}, 0x{:04X}'.format(sop, rb, ra, imm16) 
        elif (stype == 'IS'):
            return '{} r{}, r{}, {}'.format(sop, rb, ra, simm16) 
        elif (stype == 'R'):
            return '{} r{}, r{}, r{}'.format(sop, rc, ra, rb) 
        elif (stype == 'RI'):
            return '{} r{}, r{}, {}'.format(sop, rc, ra, imm5) 
        elif (stype == 'J'):
            return '{} 0x{:08X}'.format(sop, imm26*4) 
        elif (stype == 'BR'):
            return '{} {}'.format(sop, simm16) 
        elif (stype == 'SBO'):
            return '{} r{}, {}(r{})'.format(sop, rb, simm16, ra) 
        elif (stype == 'LBO'):
            return '{} r{}, {}(r{})'.format(sop, rb, simm16, ra) 
        elif (stype == 'CU'):
            
            return '{} {}, r{}, r{}, r{}'.format(sop, n, rc, ra, rb) 
        
        return sop + ' op6: {:02X}'.format(op6)