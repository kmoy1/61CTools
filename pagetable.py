import math
import time

def test_func(f):
    """Run f's doctests."""
    import doctest
    doctest.run_docstring_examples(f, globals())

class VirtualMemSystem:
    def __init__(self, pmem, pagesize, vmem = 2 ** 64, TLBEntries=16):
        """Initialize a virtual memory system with PMEM bytes physical memory (indicates address space),
        VMEM bytes of virtual memory, PAGESIZE page size.
        If VMEM is not specified, assume number of PT entries = (size of RAM / pagesize)
        """
        self.vmem = vmem #Virtual addr space. Could theoretically be infinite. 
        self.pmem = pmem #Physical addr space
        self.pagesize = pagesize #Page size. 
        self.TLBEntries = TLBEntries
        self.ppn_len = math.log2(self.pmem / self.pagesize)
        #self.PT_entries = self.vmem / self.pagesize #number of usable pages = number of page table entries.
        self.PT = {}
        self.TLB = {}
        self.memory = [] #A memory block is represented by (PPN, accessnum (For LRU))
        self.TLBHits = 0
        self.TLBMisses = 0
        self.accesses = 0
        self.pagehits = 0
        self.pagefaults = 0
        self.PTEntrySize = 0
        self.MaxPTEntries = vmem / pagesize #maximum number of PT entries. If VMEM is NOT specified, then we know there are pmem/pagesize possible VALID entries.
        self.MaxMemPages = pmem / pagesize #maximum number of pages in memory. 

    def Vaddr_breakdown(self, addr):
        """Parse virtual address into (pagenum, page offset) and return.
        NOTE: VM address breakdown really ONLY depends on page size.
        >>> A = VirtualMemSystem(2 ** 32, 2 ** 20, 2 ** 12)
        >>> A.Vaddr_breakdown(bin(0xDEADBEEF))
        >>> B = VirtualMemSystem(2 ** 64, 2 ** 32, 2 ** 12)
        """
        if addr[:2] == '0b':
            addr = addr[2:]
        pagenum_bits = int(math.log2(self.MaxPTEntries)) #Number of bits for page.
        offset_bits = int(math.log2(self.pagesize))
        assert len(addr) == pagenum_bits + offset_bits
        pagenum = int(addr[:pagenum_bits], 2)
        offset = int(addr[pagenum_bits:], 2)
        return pagenum, offset

    def PTSizeL1(self):
        """Return size (bytes) of SINGLE LEVEL page table for this VMSystem.
        ENTRY_SIZE is input in BITS. Assume 
        >>> A = VirtualMemSystem(2 ** 64, 2 ** 20, 2 ** 15)
        >>> math.log2(A.PTSizeL1(entry_size=32))
        51.0
        """
        assert self.PTEntrySize != 0, "Must set Entry size first!"
        return ((self.vmem / self.pagesize) * self.PTEntrySize)/8

    def setPTBR(self, PTBR_addr):
        """Set base table register for page table- holds address where page table begins in memory"""
        self.PTBR = PTBR_addr

    def setPTEntrySize(self, extrabits):
        """Set PT entry size to PPN length + extra bits (metadata, dirty bit), and convert back to bytes."""
        self.PTEntrySize = (self.ppn_len + extrabits)/8

    def PT_SizeL2(self, entry_size, L2BlockEntries):
        """Return size of L1 table TWO-LEVEL page table . In a two level page table, our page 
        table is broken up into fixed-size blocks with L2BLOCKENTRIES entries. These blocks make up the level 2 page table. 
        Each L1 PT entry points to a block in the L2 PT. 
        We don't need to store L2 PT as contiguous, and don't need to allocate blocks with no valid entries. 
        Remember each PT Entry "covers" a page in physical memory. 
        >>> A = VirtualMemSystem(vmem=2 ** 64, pmem=2 ** 20, pagesize=2 ** 15)
        >>> math.log2(A.PT_SizeL2(4,256))
        43.0
        """
        # pt_size = self.PT_SizeL1(entry_size)
        # num_blocks = pt_size / self.pagesize #blocks in L2 PT = number of entries in L1 PT
        coverage = L2BlockEntries * self.pagesize #Physical memory coverage (bytes) per L1 Page Table entry
        needed_L1_PTE = self.vmem / coverage
        return needed_L1_PTE * entry_size

    def valid_PTE(self):
        """Calculate (maximum) PTE for a (single-level) page table. Note we cannot have more valid page table entries than
        pages in physical memory- this just does not make sense. 
        >>> A = VirtualMemSystem(pmem=2 ** 30, pagesize=2 ** 10)
        >>> math.log2(A.valid_PTE())
        20.0
        """
        return self.pmem / self.pagesize

    def TLBReach(self):
        """Return the coverage, or the amount of memory addressable by TLB page entries for this 
        VM System.
        >>> A = VirtualMemSystem(pmem=2 ** 30, pagesize=2 ** 10, TLBEntries=8)
        >>> math.log2(A.TLBReach())
        13.0
        """
        return self.TLBEntries * self.pagesize

    def sim_access(self, addr):
        """Simulate an access of virtual memory address ADDR (bitstring). 
        Update TLB/PT as necessary and return physical memory translation.
        """
        if addr[:2] == '0b':
            addr = addr[2:]
        vpn, offset = self.Vaddr_breakdown(addr) #Break down virtual address into VPN and . 
        ppn = self.searchTLB(vpn) #Search TLB for a VPN->PPN mapping. ppn = None if not found.
        phys_addr = 0
        if not ppn: #VPN->PPN mapping not found in TLB
            ppn = self.searchPT(vpn, ppn) #Next search the page table for a mapping. Either returns or finds the next available PPN in memory (LRU)
            phys_addr = str(bin(ppn)) + str(bin(offset))
            self.accesses += 1
            return phys_addr
        else:
            #Found ppn. Concatenate with offset and return as physical address bitstring. 
            phys_addr = str(bin(ppn)) + str(bin(offset))
            self.accesses += 1
            return phys_addr

    def searchTLB(self, vpn):
        """Return value in TLB if page number maps to if it exists."""
        if vpn in self.TLB:
            self.TLBHits += 1
            #Update memory usage for ppn
            for i in range(len(self.memory)):
                page = self.memory[i]
                if page[2] == vpn:
                    self.memory[i] = (page[0], self.accesses, vpn)
                    break
            return self.TLB.get(vpn)
        else:
            self.TLBMisses += 1
            return None

    def searchPT(self, vpn, PPN_new):
        """Return physical page num in TLB if a mapping exists for VPN.
        If it does not, simulate disk access and update TLB and PT with new (VPN, PPN_NEW)"""
        if vpn in self.PT:#Mapping exists in page table. 
            #vb = self.PT.get(vpn)[1] #
            self.pagehits += 1
            #Update access time for a hit.
            #print("PAGE HIT!")
            for i in range(len(self.memory)):
                page = self.memory[i]
                if page[2] == vpn:
                    self.memory[i] = (page[0], self.accesses, vpn)
                    break

            #self.memory.append((ppn, self.accesses, vpn))
            return self.PT.get(vpn)[0]
            # else:
            #     self.pagefaults += 1
            #     ppn = self.next_available_PPN() #Get next available page number in memory to load from. 
            #     self.PT[vpn] = (ppn, 1) #Set page table.
            #     self.TLB[vpn] = ppn
            #     if len(self.memory) < self.MaxMemPages:
            #         self.memory.append((ppn, self.accesses))

        else: #Mapping does not exist. 
            self.pagefaults += 1 #Not in memory. Must load.
            ppn = self.next_available_PPN() #Get next available page number in memory to load from. 
            #LRU_ppn = self.getLRUPPN() #Get frame number to replace. 
            #Update memory, PT, and TLB
            removed_memory = False
            removed_ppn = 0
            removed_vpn = 0
            #Update memory FIRST 
            if len(self.memory) < self.MaxMemPages:
                self.memory.append((ppn, self.accesses, vpn))
            else: #Need to replace LRU frame number (PPN).
                #print("Going to replace page", ppn)
                for PPN_s, access_num, VPN_S in self.memory:
                    if PPN_s == ppn:
                        removed_ppn = PPN_s
                        removed_vpn = VPN_S
                        self.memory.remove((PPN_s,access_num, VPN_S)) #Remove LRU PTE
                        self.memory.append((ppn, self.accesses, vpn)) #Replace it with new one. 
                        break  
                removed_memory = True 
            #Update page table.
            if len(self.PT) < self.MaxPTEntries:
                self.PT[vpn] = (ppn, 1) #Set page table.
            if len(self.TLB) < self.TLBEntries:
                self.TLB[vpn] = ppn #Set page table.

            if removed_memory:
                #Need to replace an entry in TLB AND Page table.
                for VPN_s, PTE in self.PT.items():
                    if PTE[0] == removed_ppn:
                        self.PT.pop(VPN_s) #Remove LRU PTE
                        self.PT[vpn] = (ppn, 1) #Replace it with new one.
                        break
                for VPN_S, PPN_S in self.TLB.items():
                    if PPN_S == removed_ppn:
                        self.TLB.pop(VPN_S) #Remove LRU PTE
                        self.TLB[vpn] = ppn #Replace it with new one.   
                        break             
            return ppn
                
    def next_available_PPN(self):
        """Return the next available physical page number to fill (from disk)"""
        if len(self.memory) < self.MaxMemPages:
            return len(self.memory) #physical page number is simply just next index in memory. 
        else:
            return self.getLRUPPN() #Return the physical page number with the MINUMUM time stamp (least recently used)

    def getLRUPPN(self):
        """Return PPN of least recently used page in memory."""
        return min(self.memory, key=lambda frame: frame[1])[0]

    def status(self):
        print("Memory:")
        print(self.memory)
        print("TLB:")
        print(self.TLB)
        print("Page Table:")
        print(self.PT)
        print("TLB HITS:", self.TLBHits)
        print("TLB MISSES:", self.TLBMisses)
        print("PAGE HITS:", self.pagehits)
        print("PAGE FAULTS:", self.pagefaults)

def sim_accesses(system, addresses, per=1):
    """Given VM System and (int) addresses and accesses per address, simulate TLB hit/misses
    >>> A = VirtualMemSystem(pmem=2 ** 30, pagesize=2 ** 10, TLBEntries=8)
    >>> accesses = [a for a in range(0, 128, 4)]
    >>> A.sim_TLB_acc(accesses, per=2)
    HITS: 127
    MISSES: 1
    HIT RATE: 0.9921875
    """
    assert isinstance(system, VirtualMemSystem)
    pn_bits = int(math.log2(system.MaxPTEntries))
    offset_bits = int(math.log2(system.pagesize))
    pad_addr = [bin(a)[2:].zfill(pn_bits+offset_bits) for a in addresses]
    for addr in pad_addr:
        system.sim_access(addr)


# 1 GiB of RAM with 1 KiB pages
# a fully‐associative TLB that holds 8 entries and uses LRU
# Please express your answer as a power of 2 (e.g. 2^5).


test_func(VirtualMemSystem.TLBReach)