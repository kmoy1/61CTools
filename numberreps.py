import math

def test_func(f):
    """Run f's doctests."""
    import doctest
    doctest.run_docstring_examples(f, globals())

def u_reps(n):
    """Given integer N, print all UNSIGNED representations in decimal, binary, hex.
    Binary numbers are prefixed with "0b" and hex numbers are prefixed with "0x".
    >>> u_reps(0b11110001)
    DEC: 241
    BIN: 0b11110001
    HEX: 0xF1
    >>> u_reps(100)
    DEC: 100
    BIN: 0b01100100
    HEX: 0x64
    >>> u_reps(0x2A1)
    DEC: 673
    BIN: 0b001010100001
    HEX: 0x2A1
    """
    assert n >= 0 and type(n) is int, "only unsigned (nonnegative) integer arguments."
    print("DEC:", n)
    b = padded_dtob(n)
    x = "0x" + format(n, 'X')
    print("BIN:", b)#dec -> bin
    print("HEX:", x)#dec -> hex

def tc_bits(n):
    """Return the minimal number of bits needed to represent n in 2's complement.
    Mathematically, n bits can represent numbers in range [-2^(n-1), 2^(n-1) - 1]
    """
    for i in range(1,100):
        lower = -(2 ** (i-1))
        upper = (2 ** (i-1)) - 1 
        if lower <= n <= upper:
            return i 
    return 0 #Should never reach here.

def tc_reps(n, max_digits=8):
    """Given N as a decimal integer OR in string binary/hex format, print all TWO's COMPLEMENT representations 
    in decimal, binary, hex. Binary numbers are prefixed with "0b" and hex numbers 
    are prefixed with "0x".
    that the LEADING BIT IS A 1- i.e. we only care about TC reps of negative numbers 
    (positive is the same as unsigned, with just a 0 MSB).
    >>> tc_reps("0b11111101")
    DEC: -3
    BIN: 0b11111101
    HEX: 0xFD
    >>> tc_reps("0b01010101")
    DEC: 85
    BIN: 0b01010101
    HEX: 0x55
    >>> tc_reps(-13)
    DEC: -13
    BIN: 0b11110011
    HEX: 0xF3
    >>> tc_reps(121)
    DEC: 121
    BIN: 0b01111001
    HEX: 0x79
    >>> tc_reps("0xC2")
    DEC: -62
    BIN: 0b11000010
    HEX: 0xC2
    >>> tc_reps("0x65")
    DEC: 101
    BIN: 0b01100101
    HEX: 0x65
    """
    #Assume N is a binary value here. 
    d = n
    b = ""
    h = ""
    if type(n) is str:
        header, num = n[:2], n[2:]
        if header == '0b': #Handle binary
            sign_bit = num[0]
            d = 0
            if sign_bit == '1': #Handle negatives: Convert 
                bs_pad = se_pad(num) #sign-extend bit string to 4-mul
                d = -1 * (int(invert(bs_pad),2) + 1)
            else:
                bs_pad = se_pad(num) #sign-extend bit string to 4-mul
                d = int(num, base=2) #Simply take unsigned version.
            h = "0x" + ("%X" % int(bs_pad,2)) #Retain padded bits how it is.
            b = "0b" + num
            #TODO: Handle overflow.
        elif header == '0x': #Handle hex
            h_digits = len(h) * 4
            bs = htob_preserve_zeros(n) #Convert to bit string + preserve leading zeros. 
            sign_bit = bs[0]
            if sign_bit == '1':
                bs_pad = zero_pad(bs) #Same logic @ binary input.
                d = -1 * (int(invert(bs_pad),2) + 1)
            else:
                bs_pad = se_pad(bs)
                d = int(bs, base=2)#positive number.
            h = "0x" + num
            b = "0b" + bs_pad
        print("DEC:", d)
        print("BIN:", b)
        print("HEX:", h)
    else: #Integer
        b = "0b" + se_pad(dec_to_tc(n))
        d = n
        h = "0x" + ("%X" % int(b,2))
        print("DEC:", d)
        print("BIN:", b)
        print("HEX:", h)

def sam_reps(n):
    """Given integer N, print sall SIGN & MAGNITUDE representations in decimal, binary, hex.
    Binary numbers are prefixed with "0b" and hex numbers are prefixed with "0x".
    >>> sam_reps("0b00110101")
    DEC: 53
    BIN: 0b00110101
    HEX: 0x35
    Sign: +
    Magnitude: 53 (0110101)
    >>> sam_reps("0b11101101")
    DEC: -109
    BIN: 0b11101101
    HEX: 0xED
    Sign: -
    Magnitude: 109 (1101101)
    >>> sam_reps(-3)
    DEC: -3
    BIN: 0b1011
    HEX: 0xB
    Sign: -
    Magnitude: 3 (011)
    """
    pm = ""
    if type(n) is str:
        #Implement "0bXXXX" logic
        header, digits = n[:2], n[2:]
        if header == "0b":
            sign_bit, mag = digits[0], digits[1:] #Binary string (unsigned rn)
            if sign_bit == '0':
                d = int(mag, base=2)
                sign = "+"
            else:
                d = -1 * int(mag, base=2)
                sign = "-"
            b = "0b" + digits
            h = "0x" + format(int(digits,base=2), 'X')
        elif header == "0x":
            bs = bin(int(digits,base=16))[2:] #hex -> bitstring
            sign_bit, mag = bs[0], bs[1:]
            if sign_bit == '0':
                d = int(mag, base=2)
                sign = "+"
            else:
                d = -1 * int(mag, base=2)
                sign = "-"
            b = "0b" + digits
            h = "0x" + format(int(n,base=2),'X')
            #convert hex -> bin.
        pm = mag
    else: #Implement decimal logic.
        if n < 0:
            mag = bin(n)[3:]
            padded_mag = mag
            while len(padded_mag) % 3 != 0:
                padded_mag = '0' + padded_mag
            b = "0b1" + padded_mag
            sign = "-"
        else:
            mag = bin(n)[2:]
            padded_mag = mag
            while len(padded_mag) % 3 != 0:
                padded_mag = '0' + padded_mag
            b = "0b0" + padded_mag
            sign = "+"
        pm = padded_mag
        h = "0x" + format(int(b,2), 'X')
        d = n
    print("DEC:", d)
    print("BIN:", b)
    print("HEX:", h)
    print("Sign:", sign)
    print("Magnitude:", str(int(mag,2)) + " (" + str(pm) + ")" )

def bias_reps(n, bias=0):
    """Given unsigned integer N and bias B (default 0, or unsigned) print all SIGN & MAGNITUDE representations 
    in decimal, binary, hex. We subtract BIAS from N.
    Binary numbers are prefixed with "0b" and hex numbers are prefixed with "0x".
    >>> bias_reps(10, 5)
    DEC: 5
    BIN: 0b1010

    """
    if type(n) is str:
        #Implement "0bXXXX" logic
        b = bin(n)[2:] #Binary string (unsigned rn)
        sign_bit = b[0]
        print("DEC:", d)
        print("BIN:", b)
        print("HEX:", h)
    else: #Implement decimal logic.
        d = n-bias
        b = bin(n)
        h = "0x" + ("%X" % int(b,2))

def opt_bias(upper):
    """Returns optimal bias for [0, UPPER], s.t. we
    represent an equal number of positive and negative numbers."""
    return None


#####HELPER FUNCS#####

def twos_comp(val, bits):
    """Convert decimal to 2's complement"""
    if (val & (1 << (bits - 1))) != 0: 
        val = val - (1 << bits)
    return val

def to_twoscomplement(n):
    #Figure out minimum number of bits needed to represent n
    bits = roundup(math.log2(abs(n)))
    if n < 0:
        n = (1 << bits) + n
    formatstring = '{:0%ib}' % bits
    return formatstring.format(n)

def num_bits(n):
    """Return the number of bits needed to represent N"""
    return math.floor(math.log2(abs(N))) + 1

def btod(s):
    """Helper func that converts binary string S to unsigned decimal.
    >>> btod("0b11010")
    26
    >>> btod("10101")
    21  
    """
    if s[0:2] == "0b":
        s = s[2:]    
    return int(s, 2)


def padded_dtob(x):
    """Given integer x, return a binary string padded so bit width is
    a multiple of 4."""
    padded_bw = roundup(len(bin(x)) - 2)
    true_bw = len(bin(x))-2
    dtob = bin(x)[2:]
    while len(dtob) < padded_bw:
        dtob = '0' + dtob
    dtob = '0b' + dtob
    return dtob

def roundup(x, base=4):
    """Helper func that rounds X UP to nearest multiple
    of 4."""
    return base * math.ceil(x/base)

def invert(bs):
    """Given bit string BS, return bit string with every bit negated."""
    return ''.join('1' if x == '0' else '0' for x in bs)

def se_pad(bs, mult=4):
    """Sign-extend a bit string to have length be a multiple 
    of MULT.
    >>> se_pad('10101')
    '11110101'
    >>> se_pad('0b010111')
    '00010111'
    """
    if bs[:2] == '0b':
        bs = bs[2:]
    sign_bit = bs[0]
    while len(bs) % mult != 0:
        bs = sign_bit + bs
    return bs

def tc_to_dec(x, n=8):
    """Convert two's complement binary OR hex string with N bits to decimal.
    >>> tc_to_dec("0b101010")
    -22
    >>> tc_to_dec("01011")
    11
    >>> tc_to_dec("0x55")
    85
    >>> tc_to_dec("0x88")
    -120
    """
    if x[:2] == "0x":
        h_digits = len(x[2:]) * 4
        bs = htob(x) #Convert to bit string + preserve leading zeros. 
        sign_bit = bs[0]
        if sign_bit == '1':
            #bs_pad = zero_pad(bs) #Same logic @ binary input.
            d = -1 * (int(invert(bs),2) + 1)
            return d
        else:
            bs_pad = se_pad(bs)
            d = int(bs, base=2)#positive number.
            return d
    elif x[:2] == "0b":
        x = x[2:]
    n = len(x)
    sign_bit = x[0]
    x = x[1:]
    if sign_bit == '0':
        return int(x, base=2)
    else:
        return -(2 ** (n-1)) + int(x, base=2)

def dec_to_tc(x, n=8):
    """Convert decimal to two's complement binary string, and sign-extend it to fit N bits (8 by default)
    >>> dec_to_tc(121)
    '0b01111001'
    >>> dec_to_tc(-13)
    '0b10011'
    """
    nbits = x.bit_length() + 1
    bs = f"{x & ((1 << nbits) - 1):0{nbits}b}"
    return "0b" + bs

def zero_pad(bs, mult=4):
    """Zero-pad a bit string to have length be a multiple 
    of MULT.
    >>> zero_pad('10101')
    '00010101'
    >>> zero_pad('0b01011')
    '00001011'
    """
    if bs[:2] == '0b':
        bs = bs[2:]
    while len(bs) % mult != 0:
        bs = '0' + bs
    return bs

def htob_preserve_zeros(h):
    """Convert hex to binary, preserve leading zeros if any.
    >>> htob_preserve_zeros('0x65')
    '01100101'
    """
    assert h[:2] == '0x', 'h must be in string 0x(...) form!'
    h = h[2:]
    b = (bin(int(h, 16))[2:]).zfill(len(h) * 4)
    return b

def htob(h):
    """Convert hex to binary, preserve leading zeros if any.
    >>> htob_preserve_zeros('0x65')
    '01100101'
    """
    assert h[:2] == '0x', 'h must be in string 0x(...) form!'
    h = h[2:]
    b = (bin(int(h, 16))[2:])
    return b

def overflows_tc(x1, x2, op, n):
    """Return true if x1 + x2 OR x1 - x2 causes an overflow with n bits. 
    Assume x1 and x2 are in two's complement string form.
    >>> overflows_tc("0b100011", "0b111010", '+', 6)
    True
    >>> overflows_tc("0x3B", "0x06", '+', 6)
    False
    >>> overflows_tc("0b011001", "0b000111", '-', 6)
    False
    """
    if op == '+':
        res = tc_to_dec(x1) + tc_to_dec(x2)
    elif op == '-':
        res = tc_to_dec(x1) - tc_to_dec(x2)

    lower_bd = -1 * (2 ** (n-1))
    upper_bd = (2 ** (n-1)) - 1
    return res not in range(lower_bd, upper_bd) #if NOT in bounds, OVERFLOW

def bs_to_arr1(bs, k, bendian = False):
    """Convert bitstring BS to a list (array) of K UNSIGNED integers and return it.
    Ordering depends on BENDIAN optional parameter
    (default little endian). Ideally, BS should be a multiple of k but last element is zero-padded to be 8 bits
     if it is not. 
    >>> A = bs_to_arr1("0b11111010000000000000000000000011", 8)
    >>> A[0]
    3
    >>> A[2]
    0
    >>> A[3]
    250
    """
    last_k_ind = len(bs)-(len(bs) % k) #Last index of bit string that is a multiple of k (L to R)
    if bs[:2] == "0b":
        bs = bs[2:]
    splits = [bs[i:i+k] for i in range(0, last_k_ind, k)]
    if len(bs) % k != 0:
        #Get remaining chunk of list, zeropad, 
        chunk = bs[len(bs)-(len(bs) % k):len(bs)]
        num = int(zero_pad(chunk, k), base=2)
        A = splits + [num]
    else:
        A = splits
    if bendian:
        return [int(x,2) for x in A]
    else:
        A.reverse()
        return [int(x,2) for x in A]

test_func(bs_to_arr1)
