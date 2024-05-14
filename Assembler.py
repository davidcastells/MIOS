# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 15:53:10 2024

@author: dcr
"""

#  Check info from https://www-ug.eecg.toronto.edu/msl/manuals/n2cpu_nii51017.pdf
 
class BV:
    
    def __init__(self, length, value):
        self.l = length
        self.v = ((1 << length)-1) & value

    @staticmethod
    def concatenate(els):
        '''
        Concatenate 
        '''
        v = 0
        tl = 0
        for bv in els:
            tl += bv.l
            v = v << bv.l
            v = v | bv.v
            
        return BV(tl, v)
            

class Assembler:

    @staticmethod
    def beq(ra, rb, offset):
        return BV.concatenate([BV(6, 0x26), BV(16, offset), BV(5, rb), BV(5, ra)])
    
    @staticmethod
    def bne(ra, rb, offset):
        return BV.concatenate([BV(6, 0x1E), BV(16, offset), BV(5, rb), BV(5, ra)])

    @staticmethod
    def blt(ra, rb, offset):
        return BV.concatenate([BV(6, 0x16), BV(16, offset), BV(5, rb), BV(5, ra)])

    @staticmethod
    def bge(ra, rb, offset):
        return BV.concatenate([BV(6, 0x0e), BV(16, offset), BV(5, rb), BV(5, ra)])

    @staticmethod
    def ori(rb, ra, imm):
        return BV.concatenate([BV(6, 0x14), BV(16, imm), BV(5, rb), BV(5, ra)])

    @staticmethod
    def orhi(rb, ra, imm):
        return BV.concatenate([BV(6, 0x34), BV(16, imm), BV(5, rb), BV(5, ra)])

    @staticmethod
    def and(rc, ra, rb):
        return BV.concatenate([BV(6, 0x3A), BV(5, 0), BV(6, 0x0E), BV(5, rc), BV(5, rb), BV(5, ra)])

    @staticmethod
    def andi(rb, ra, imm):
        return BV.concatenate([BV(6, 0x0C), BV(16, imm), BV(5, rb), BV(5, ra)])

    @staticmethod
    def or(rc, ra, rb):
        return BV.concatenate([BV(6, 0x3A), BV(5, 0), BV(6, 0x16), BV(5, rc), BV(5, rb), BV(5, ra)])

    @staticmethod
    def nor(rc, ra, rb):
        return BV.concatenate([BV(6, 0x3A), BV(5, 0), BV(6, 0x06), BV(5, rc), BV(5, rb), BV(5, ra)])

    @staticmethod
    def add(rc, ra, rb):
        return BV.concatenate([BV(6, 0x3A), BV(5, 0), BV(6, 0x31), BV(5, rc), BV(5, rb), BV(5, ra)])

    @staticmethod
    def addi(rb, ra, imm):
        return BV.concatenate([BV(6, 0x04), BV(16, imm), BV(5, rb), BV(5, ra)])

    @staticmethod
    def sub(rc, ra, rb):
        return BV.concatenate([BV(6, 0x3A), BV(5, 0), BV(6, 0x39), BV(5, rc), BV(5, rb), BV(5, ra)])

    @staticmethod
    def mul(rc, ra, rb):
        return BV.concatenate([BV(6, 0x3A), BV(5, 0), BV(6, 0x27), BV(5, rc), BV(5, rb), BV(5, ra)])

    @staticmethod
    def ldw(rb, offset, ra):
        return BV.concatenate([BV(6, 0x17), BV(16, offset), BV(5, rb), BV(5, ra)])
    
    @staticmethod
    def ldwio(rb, offset, ra):
        return BV.concatenate([BV(6, 0x37), BV(16, offset), BV(5, rb), BV(5, ra)])

    @staticmethod
    def stw(rb, offset, ra):
        return BV.concatenate([BV(6, 0x15), BV(16, offset), BV(5, rb), BV(5, ra)])

    @staticmethod
    def stwio(rb, offset, ra):
        return BV.concatenate([BV(6, 0x35), BV(16, offset), BV(5, rb), BV(5, ra)])

    @staticmethod
    def stb(rb, offset, ra):
        return BV.concatenate([BV(6, 0x05), BV(16, offset), BV(5, rb), BV(5, ra)])

    @staticmethod
    public static BV br(offset):
        return BV.concatenate([BV(6, 0x06), BV(16, offset), BV(10,0)])

    @staticmethod
    def ldb(rb, offset, ra):
        return BV.concatenate([BV(6, 0x07), BV(16, offset), BV(5, rb), BV(5, ra)])

    @staticmethod
    def ldbu(rb, offset, ra):
        return BV.concatenate([BV(6, 0x03), BV(16, offset), BV(5, rb), BV(5, ra)])

    @staticmethod
    def custom(n, rc, ra, rb):
        return BV.concatenate([BV(6, 0x32), BV(8, n), BV(3, 7), BV(5, rc), BV(5, rb), BV(5, ra)])

    @staticmethod
    def roli(rc, ra, imm):
        return BV.concatenate([BV(6, 0x3A), BV(5, imm), BV(6, 0x02), BV(5, rc), BV(5, 0), BV(5, ra)])

    @staticmethod
    def srli(int rc, int ra, int imm):
        return BV.concatenate([BV(6, 0x3A), BV(5, imm), BV(6, 0x1A), BV(5, rc), BV(5, 0), BV(5, ra)])

    @staticmethod
    def call(int imm)
        return BV.concatenate([BV(6, 0x0), BV(26, imm >> 2)])

    @staticmethod
    def ret():
        return BV.concatenate({BV(6, 0x3A), BV(5, 0), BV(6, 0x05), BV(5, 0), BV(5, 0), BV(5, 0x1f)])

    @staticmethod
    def invalid():
        return BV.concatenate(32, -1);
