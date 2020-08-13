def hex_to_instruction(bs):
    """Ultimate converter of binary to RISC-V hex"""
    if bs[:2] == '0b':
        bs = bs[2:]
    bs_ins = bs[::-1] #Reverse string so that index 0 corresponds to bit 0.
    opcode = bs_ins[0:7]
    rd = bs_ins[7:12]
    funct3 = bs_ins[12:15]
