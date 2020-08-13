import math

def test_func(f):
    """Run f's doctests."""
    import doctest
    doctest.run_docstring_examples(f, globals())

def stoms(x):
    """Convert x in standard SI units to milli-units"""
    return x * 1000

def mstos(x):
    """Convert x in milli-units to standard SI units"""
    return x / 1000


def AAT(tracks, ATT, a_spd, CPT, TR, TA):
    """Calculate average access time, in SECONDS for a disk 
    given parameters:
    - TRACKS: Number of tracks
    - ATT: All-track time, or time for head to move across ALL tracks (seconds)
    - A_SPD: Angular speed, (revolutions/second)
    - CPT: Controller processing time (seconds)
    - TR: Transfer rate (bytes/second)
    - TA: Transfer amount (bytes)
    (Avg) Disk Access Time = Seek Time + Rotation Time + Transfer Time + Controller Overhead
    >>> AAT(900, 0.003, 166, 0.001, 1000000, 1000)
    0.0060120481927710846
    """
    seek_time = ATT / 3 #Time to cross 1/3 of all tracks.
    print(seek_time)
    rotation_time = 1 / (a_spd * 2) #Time for 1/2 rotation.
    transfer_time = TA / TR #T = D/R
    return seek_time + rotation_time + transfer_time + CPT

def poll_time1(p_freq, poll_time, IO_PR):
    """Print % of processor time to loop-wait poll given parameters:
    - P_FREQ: Processor speed (clock cycles/s)
    - POLL_TIME: Time for procesor to COMPLETE polling operation (clock cycles per poll). Includes polling CODE in addition to time.
    - IO_PR: IO Device poll frequency (polls/s)
    >>> poll_time1(10 ** 9, 400, 30)
    Poll Frequency: 12000 clock cycles/s
    Percent of Processor Time: 0.001200%
    >>> poll_time1(10 ** 9, 400, 10 ** 6)
    Poll Frequency: 400000000 clock cycles/s
    Percent of Processor Time: 40.000000%
    """
    poll_freq = IO_PR * poll_time
    print("Poll Frequency:", poll_freq, "clock cycles/s")
    print("Percent of Processor Time:", "%f" % float(str(100 * poll_freq / p_freq)) + "%")

def interrupt_time_PIO(p_freq, interrupt_time, IO_TP, transfer_amt, IO_activity):
    """Calculate % of processor time to INTERRUPT (by disk) given parameters:
    - P_FREQ: Processor speed (clock cycles/s)
    - INTERRUPT_TIME: Overhead time for processor to COMPLETE (5 stages of) interrupt operation (clock cycles / interrupt)
    - IO_TP: IO device throughput (bytes/s)
    - TRANSFER_AMT: Transfer amount from IO device needed to signal  an interrupt (bytes)
    - IO_ACTIVITY: Proportion of time IO device is active during program 
    >>> interrupt_time_PIO(10 ** 9, 500, 16 * 10 ** 6, 16, 0.05)
    2.5% of CPU occupied
    """
    interrupt_rate = IO_activity * (IO_TP / transfer_amt) # Interrupts/s
    icc = interrupt_rate * interrupt_time #interrupt clock consumption (clock cycles / s)
    print(str(icc * 100 / p_freq)+ "% of CPU occupied")

def interrupt_time_DMA(p_freq, DMA_time, IO_TP, transfer_amt):
    """Calculate % of processor time for DMA given parameters:
    - P_FREQ: Processor speed (clock cycles/s)
    - DMA_TIME: DMA Engine overhead (clock cycles / transfer)
    - IO_TP: IO device throughput (bytes/s)
    - TRANSFER_AMT: Transfer amount for DMA needed before DMA engine interrupts CPU.
    Note IO device activity is no longer important! We have an entire separate unit to handle this shit!
    >>> interrupt_time_DMA(10 ** 9, 500, 16 * 10 ** 6, 4000)
    0.2% of CPU occupied
    """
    interrupt_rate = IO_TP / transfer_amt #interrupts/s
    time_taken = interrupt_rate * DMA_time #clock cycles / s
    print(str(time_taken * 100 / p_freq)+ "% of CPU occupied")


test_func(interrupt_time_DMA)