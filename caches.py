import math
import struct
import numberreps as reps
from random import randrange

def test_func(f):
    """Run f's doctests."""
    import doctest
    doctest.run_docstring_examples(f, globals())

class Cache:
    def __init__(self, cache_size, block_size, address_size):
        """Given cache size and block size in bytes and address size in bits, create cache object."""
        self.cache_size = int(cache_size)
        self.block_size = int(block_size)
        self.address_size = int(address_size)
        self.hits = 0
        self.misses = 0
        self.accesses = 0

class SACache(Cache): #SET ASSOCIATIVE CACHE
    def __init__(self, cache_size, block_size, address_size, N, wpolicy='WT'):
        """Initialize an N-way set associative cache. Now blocks map
        to a SET via index and is placed anywhere in that set."""
        super().__init__(cache_size, block_size, address_size)
        self.assoc = N
        self.wpolicy = wpolicy
        self.initialize_cache()

    def TIO_DM(self):
        """Print TIO Breakdown for a direct-mapped cache of size CACHE_SIZE (bytes)
        with block size BLOCK_SIZE (bytes) using ADDRESS_SIZE-bit byte addresses. 
        Remember index bits used to access each set, and in an N-way assoc. cache, each set contains N blocks. 
        >>> A = SACache(16, 4, 6, 2, wpolicy='WT')
        >>> A.TIO_DM()
        (3, 1, 2)
        >>> B = SACache(32768, 8, 32, 4, wpolicy='WT')
        >>> A.TIO_DM()
        (3, 1, 2)
        """
        num_sets = int(self.cache_size / (self.block_size * self.assoc))
        index_bits = int(math.log2(num_sets))
        offset_bits = int(math.log2(self.block_size))
        tag_bits = int(self.address_size) - index_bits - offset_bits
        return (tag_bits, index_bits, offset_bits)
    def breakdown(self, addr):
        if bd[:2] == '0b':
            bd = bd[2:]
        bd = self.TIO_DM()
        return int(addr[:bd[0]],2), int(addr[bd[0]:bd[0]+bd[1]],2), int(addr[bd[0]+bd[1]:],2)
    def initialize_cache(self):
        """Initialize cache, where each cache slot: (valid bit, tag, (d1, d2))"""
        num_sets = int(self.cache_size / (self.block_size * self.assoc))
        self.table = [[(0, 0, (0,0), 0) for i in range(self.assoc)] for i in range(num_sets)]

    def cache_bits(self):
        """Return size of N-way SA cache in BITS. Remember cache bits = 
        #sets * (#slots * bits/slot). 
        >>> A = SACache(16, 4, 6, 2, wpolicy='WT')
        >>> A.cache_bits()
        148
        """
        num_sets = int(self.cache_size / (self.block_size * self.assoc))
        slots_per_set = self.assoc
        bd = self.TIO_DM()
        bits_per_slot = 8 * (2 ** bd[2]) + bd[0] + 1
        if self.wpolicy == 'WT': #Need replacement policy bit (LRU)
            bits_per_slot += 1
        return num_sets * slots_per_set * bits_per_slot

    def sim_access(self, addr, access_num):
        """Simulate a single access of a block at memory address ADDR (bitstring) into memory.
        >>> A = SACache(16, 4, 6, 2, wpolicy='WT')
        >>> A.sim_access('000000', 1)
        """
        if isinstance(addr, int):
            addr = bin(addr)[2:].zfill(self.address_size)
        tag, ind, off = self.parseAddr(addr)
        cset = self.table[ind]
        vb = 0
        hit_slot = (0, 0, (0,0), 0)
        found_slot = False

        for slot in cset:
            if tag == slot[1]: 
                hit_slot = slot
                found_slot = True
                vb = slot[0]
                break

        if vb and found_slot and int(addr,2) in range(hit_slot[2][0], hit_slot[2][1]):
            self.hits += 1

        else:
            self.misses += 1
            num_valid_slots = sum([slot[0] for slot in cset])
            if num_valid_slots < self.assoc:
                #Replace a slot with VB 0.
                init_ind = 0
                for slot in cset:
                    if slot[0] == 0:
                        break
                    init_ind += 1
                cset[init_ind] = (1, tag, blocksize_align(int(addr,2), self.block_size), access_num)
            else:#Need to replace. 
                LRU_ind = cset.index(min(cset, key=lambda slot: slot[3]))
                cset[LRU_ind] = (1, tag, blocksize_align(int(addr,2), self.block_size), access_num)
        self.accesses += 1

    def parseAddr(self, address):
        """Given binary address, return corresponding (tag, index, offset) for DM cache as 3-element tuple.
        >>> A = SACache(16, 4, 6, 2, wpolicy='WT')
        >>> A.parseAddr('000010')
        (0, 0, 2)
        >>> A.parseAddr('000100')
        (0, 1, 0)
        """
        if address[:2] == '0b':
            address = address[2:]
        assert len(address) == self.address_size
        bd = self.TIO_DM()
        tag = address[:bd[0]]
        index = address[bd[0]:bd[0]+bd[1]]
        offset = address[bd[0]+bd[1]:]
        return int(tag,2), int(index,2), int(offset,2)

    def __str__(self):
        c = ''
        for i in range(len(self.table)):
            c += str(i)+ ": " + str(self.table[i]) + "\n"
        c += 'HITS: ' + str(self.hits) + '\n'
        c += 'MISSES: ' + str(self.misses) + '\n'
        c += 'HIT RATE: ' + str(self.hits / self.accesses)
        return '---CACHE TABLE---\n' + c

class DMCache(Cache): #DIRECT MAPPED CACHE.
    def __init__(self, cache_size, block_size, address_size):
        super().__init__(cache_size, block_size, address_size)
        self.initialize_cache()

    def TIO_DM(self):
        """Return TIO Breakdown for a direct-mapped cache of size CACHE_SIZE (bytes)
        with block size BLOCK_SIZE (bytes) using ADDRESS_SIZE-bit byte addresses. 
        Remember index bits used to access each set, and in a DM cache, each set contains one block. 
        Offset bits are used to access bytes
        in a block. Tag bits are the rest- used to differentiate (and verify) memory addresses that map 
        to the same cache slot. 
        >>> A = DMCache(2 ** 12, 2 ** 2, 16)
        >>> A.TIO_DM()
        (4, 10, 2)
        """
        num_blocks = int(self.cache_size / self.block_size)
        index_bits = int(math.log2(num_blocks))
        offset_bits = int(math.log2(self.block_size))
        tag_bits = int(self.address_size) - index_bits - offset_bits
        return (tag_bits, index_bits, offset_bits)

    def initialize_cache(self):
        """Initialize cache, where each cache slot: (valid bit, tag, (d1, d2), LRU)"""
        num_blocks = int(self.cache_size / self.block_size)
        # if LRU:
        #     self.table = [(0,0,(0,0), i) for i in range(num_blocks)]#last elmt of slot is for LRU number!
        self.table = [(0,0,(0,0)) for i in range(num_blocks)]

    def parseAddr(self, address):
        """Given binary address, return corresponding (tag, index, offset) for DM cache as 3-element tuple.
        >>> A = DMCache(16, 4, math.log2(64))
        >>> A.TIO_DM()
        (2, 2, 2)
        >>> A.parseAddr(reps.zero_pad(bin(0x000000), A.address_size))
        (0, 0, 0)
        >>> A.parseAddr(reps.zero_pad('000010', A.address_size))
        (0, 0, 2)
        """
        if address[:2] == '0b':
            address = address[2:]
        assert len(address) == self.address_size
        bd = self.TIO_DM()
        tag = address[:bd[0]]
        index = address[bd[0]:bd[0]+bd[1]]
        offset = address[bd[0]+bd[1]:]
        return int(tag,2), int(index,2), int(offset,2)

    def cache_bits(self):
        """Return size of DM cache in BITS. Remember cache bits = 
        # slots * (number of bits in each slot = 
        8 * blocksizebytes + tag bits + valid bit). 
        >>> A = DMCache(16, 4, math.log2(64))
        >>> A.cache_bits()
        140
        """
        bd = self.TIO_DM()
        return 2 ** bd[1] * (8 * (2 ** bd[2]) + bd[0] + 1)

    def sim_access(self, addr):
        """Simulate a single access of a block at memory address ADDR (bitstring) into memory.
        >>> A = DMCache(16, 4, math.log2(64))
        >>> A.sim_access('000000')
        >>> A.sim_access('000010')
        """
        if isinstance(addr, int):
            addr = bin(addr)[2:].zfill(self.address_size)
        tag, ind, off = self.parseAddr(addr)
        vb, tbits = self.table[ind][0], self.table[ind][1]
        if vb and tbits == tag and int(addr,2) in range(self.table[ind][2][0], self.table[ind][2][1]):
            self.hits += 1
        else:
            self.misses += 1
            self.table[ind] = (1, tag, blocksize_align(int(addr,2), self.block_size))
        self.accesses += 1

    def clear_cache(self):
        self.initialize_cache()

    def __str__(self):
        c = ''
        for i in range(len(self.table)):
            c += str(i)+ ": " + str(self.table[i]) + "\n"
        c += 'HITS: ' + str(self.hits) + '\n'
        c += 'MISSES: ' + str(self.misses) + '\n'
        c += 'HIT RATE: ' + str(self.hits / self.accesses)
        return '---CACHE TABLE---\n' + c

def blocksize_align(addr, blocksize):
    """Return blocksize-aligned boundaries for memory access.
    >>> blocksize_align(20, 8)
    (16, 23)
    """
    return addr - (addr % blocksize), addr - (addr % blocksize) + blocksize - 1

def printcache(cache):
    for i in range(len(cache)):
        print(str(i)+ ":", cache[i])

test_func(DMCache.TIO_DM)

def sim_accesses(cache, accesses):
    """Simulate cache accesses on cache object CACHE, with memory addresses specified by list ACCESSES (in order).
    >>> A = DMCache(16, 4, math.log2(64))
    >>> sim_accesses(A, [0,2,4,8,20,16,0,2])
    ---CACHE TABLE---
    0: (1, 0, (0, 3))
    1: (1, 1, (20, 23))
    2: (1, 0, (8, 11))
    3: (0, 0, (0, 0))
    HITS: 2
    MISSES: 6
    HIT RATE: 0.25
    >>> B = SACache(16, 4, 6, 2, wpolicy='WT')
    >>> sim_accesses(B, [0,2,4,8,20,16,0,2])
    ---CACHE TABLE---
    0: [(1, 2, (16, 19), 5), (1, 0, (0, 3), 6)]
    1: [(1, 0, (4, 7), 2), (1, 2, (20, 23), 4)]
    HITS: 2
    MISSES: 6
    HIT RATE: 0.25
    """
    assert isinstance(cache, Cache)
    if isinstance(cache, SACache):
        for i in range(len(accesses)):
            cache.sim_access(accesses[i],i)
    else:
        for addr in accesses:
            cache.sim_access(addr)
    print(cache)


def AMAT(HT, MR, MT):
    """Calculate average memory access time for a cache."""
    return HT + MR * MT

test_func(sim_accesses)