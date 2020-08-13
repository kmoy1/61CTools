import math
import struct

def test_func(f):
    """Run f's doctests."""
    import doctest
    doctest.run_docstring_examples(f, globals())

def bs_to_float(bs, expb=8, sig=23, custom_bias = 0):
    """Convert a bitstring to (IEEE-754 Single precision FP by default) float with EXPB exponent bits and 
    SIG significand/mantissa bits. Assume bias of 2^(EXPB-1)-1, subtracted from exponent. Remember we bias
    because exponents have to be signed values in order to rep positive and negative exponents.
    >>> bs_to_float(bin(0xFFF))
    0.15625
    """
    if bs[:2] == '0b':
        bs = bs[2:]
    #assert len(bs) == expb + sig + 1
    sign = 1 if bs[expb+sig] == '1' else 0
    bias = (2 ** (expb-1))-1 if custom_bias == 0 else custom_bias
    exponent = int(bs[1:expb+1],2) - bias
    mantissa_b = bs[1+expb:len(bs)]
    mantissa = 1
    print("EXP:", exponent)
    for i in range(len(mantissa_b)):
        mantissa += int(mantissa_b[i],2) * (2 ** (-(i+1)))
        if int(mantissa_b[i],2):
            print("2^", i+1)
    return ((-1) ** sign) * (2 ** exponent) * mantissa

def denorm_to_float_sn(bs, expb=8, sig=23, custom_bias = 0):
    """Convert DENORMALIZED binary to float with EXPB exponent bits and 
    SIG significand/mantissa bits. Assume bias of 2^(EXPB-1)-1, subtracted from exponent. Remember we bias
    because exponents have to be signed values in order to rep positive and negative exponents.
    """
    if bs[:2] == '0b':
        bs = bs[2:]
    #assert len(bs) == expb + sig + 1
    sign = 1 if bs[expb+sig] == '1' else 0
    bias = (2 ** (expb-1))-1 if custom_bias == 0 else custom_bias
    exponent = 1 - bias #Exponent bits are 0, so implicit exponent is constant. 
    mantissa_b = bs[1+expb:len(bs)]
    # for i in range(len(mantissa_b)):
    #     mantissa += int(mantissa_b[i],2) * (2 ** (-(i+1)))
    print(sign + '0.' + mantissa_b + ' * 2 ^ ' + str(exponent))

def bs_to_float_sn(bs, expb=8, sig=23, custom_bias=0):
    """Convert a bitstring to (IEEE-754 Single precision FP by default) float with EXPB exponent bits and 
    SIG significand/mantissa bits. Assume bias of 2^(EXPB-1)-1, subtracted from exponent. Return BINARY
    standardized notation of string.
    >>> bs_to_float_sn(bin(0xFA000003), 7, 24, 64)
    -1.000000000000000000000011 * 2 ^ 58
    """
    if bs[:2] == '0b':
        bs = bs[2:]
    #assert len(bs) == expb + sig + 1
    sign = '-' if bs[expb+sig] == '1' else '+'
    bias = (2 ** (expb-1))-1 if custom_bias == 0 else custom_bias
    exponent = int(bs[1:expb+1],2) - bias
    mantissa_b = bs[1+expb:len(bs)]
    mantissa = 1
    # for i in range(len(mantissa_b)):
    #     mantissa += int(mantissa_b[i],2) * (2 ** (-(i+1)))

    print(sign + '1.' + mantissa_b + ' * 2 ^ ' + str(exponent))

def ftobIEEE(f):
    """Given float, print IEEE-754 single-precision binary and hex representations.
    >>> ftobIEEE(0.15625)
    0b00111110001000000000000000000000
    0x3E200000
    """
    bs = "0b" + ''.join(bin(c).replace('0b', '').rjust(8, '0') for c in struct.pack('!f', f))
    print(bs)
    print("0x{:X}".format(int(bs,2)))

def ftob_custom(f, expb=8, sig=23, custom_bias=0):
    """Given float F, and custom exponent + mantissa bit widths, 
    print IEEE-754 single-precision binary and hex representations. 
    """
    pass


test_func(ftobIEEE)