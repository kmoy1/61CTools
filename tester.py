import pagetable as pt
import math
import floats
import caches 

#Consider a system with 4 GiB of physical memory and 64 GiB of Virtual Memory. 
#The page size is 4 KiB.
#Recall that the page table is stored in physical memory and consists of PTEs.

# A = pt.VirtualMemSystem(pmem=2 ** 32, vmem=2**36, pagesize=2**12)
# #If, for each PTE, we choose to also store 12 bits of metadata 
# #(e.g. permission bits, dirty bit),how many page table entries can we now store on a page?
# A.setPTEntrySize(12)
# print(A.pagesize / A.PTEntrySize)
# #Assume each page can store 2048 PTEs. Page, PMEM, VMEM unchanged
# #How many pages does our page table occupy if we have a single level page table 
# #which has only one valid data page?
# occupied_L1_PT = A.MaxPTEntries * (1/2048) #PTEs * (pages/PTE)
# #How many pages does our page table occupy 
# #(aka how many valid (active) pages is ourpage table) 
# #if we have a two level page table which has only one valid data page? 
# #Each level uses an equal amount of bits of the page number

# print(floats.bs_to_float(bin(0xFF000003), expb=8, sig=23, custom_bias = 0))

A = caches.SACache(128, 16, 20, 2)
B = caches.SACache(128, 16, 20, 2)
print(A.parseAddr(bin(0xA0000)))

C = pt.VirtualMemSystem(pmem=2**32, vmem=2**24, pagesize=2**12)
C.setPTEntrySize(12)
print(int(math.log2(C.MaxPTEntries)))
print(int(math.log2(C.pagesize)))