__author__ = 'mfrancis'
import sys
import time
import argparse

import RPi.GPIO as GPIO

"""This needs to be run as root.

Raspberry Pi Pins

wire - pin - port - purpose

red - 2 - 5V
brown - 6 - GND

orange - 3 - GPIO2 - INCR
yellow - 5 - GPIO3 - RESET
green -7 - GPIO4 - WRITE
black1 - 11 - GPIO17 - READ

white1 - 13 - GPIO27 - D0
grey1 - 15 - GPIO22 - D1
blue1 - 12 - GPIO18 - D2
purple1 - 16 - GPIO23 - D3
purple2 - 24 - GPIO8 - D4
blue2 - 26 - GPIO7 - D5
grey2 - 23 - GPIO11 - D6
white2 - 21 - GPIO9 - D7

black2 - 19 - GPIO10 - LED
"""
INCR = 3
RESET = 5
WRITE = 7
READ = 11
LED = 19

D0 = 13
D1 = 15
D2 = 12
D3 = 16
D4 = 24
D5 = 26
D6 = 23
D7 = 21

D_ports = [D0,D1,D2,D3,D4,D5,D6,D7]
ctrl_ports = [INCR, RESET, LED, WRITE, READ]

GPIO.setmode(GPIO.BOARD)

for port in ctrl_ports:
    GPIO.setup(port, GPIO.OUT)

# Start with the D-ports as input for safety
for port in D_ports:
    GPIO.setup(port, GPIO.IN)


def on(pin):
    """Turn pin on"""
    GPIO.output(pin,1)

def off(pin):
    """Turn pin off"""
    GPIO.output(pin,0)

def set(pin, val=1):
    """set pin to value 0|1"""
    if val not in [0,1]:
        raise RuntimeError
    GPIO.output(pin,val)

def pulse_hi(pin, length=0.00001):
    """Pulse pin hi-lo for length seconds""" 
    on(pin)
    time.sleep(length)
    off(pin)
    time.sleep(length)

def pulse(*args, **kwargs):
    pulse_hi(args, kwargs)

def pulse_lo(pin, length=0.00001):
    """Pulse pin lo-hi for length seconds"""
    off(pin)
    time.sleep(length)
    on(pin)
    time.sleep(length)

def incr(n=1):
    """Increment the address by n (defaults to 1)"""
    for i in xrange(n):
        pulse_hi(INCR)

def read(type='hex', inc=False):
    """Read byte at current address"""
    bitstring = ''
    for i in [D7,D6,D5,D4,D3,D2,D1,D0]:
        bitstring += str(GPIO.input(i))
    if type == 'hex':
        rval = "Ox%02x" % (int(bitstring,2))
    elif type == "int":
        rval = int(bitstring,2)
    elif type == "bin":
        rval = "{0:b}".format(int(bitstring,2))
    else:
        rval = chr(int(bitstring,2))
    if inc:
        incr()
    return rval

def find(address=0):
    """Set current address"""
    pulse_hi(RESET)
    for i in xrange(address):
        incr()

def dump(start=0, end=0x2000):
    """Dump contents from start to end.
    aaaa 00 01 02 03 04 05 06 07 AAAAAAAA
    """
    find(start)
    address = start
    while address < end:
        # build list of 8 bytes with their ascii repr
        byte_list = [read(type='int', inc=True) for i in range(8)]
        ascii_repr = ''.join([(unichr(b) if b>31 and b<127 else '.') 
                                        for b in byte_list])
        byte_string = ' '.join(['%02X' % i for i in byte_list])
        print "%04X %s %s" % (address, byte_string, ascii_repr)
        address += 8


def write(byte, inc=False):
    """Write byte to current address."""
    # Make the D-ports output
    for port in D_ports:
        GPIO.setup(port, GPIO.OUT)

    # write the byte as zero-padded binary
    byte_string = '{0:08b}'.format(byte)
    # put the reversed bits on the D-pins
    for i,b in enumerate(byte_string[::-1]):
        set(D_ports[i], int(b))
    # READ to HI (inactive)
    on(READ)
    # pulse WR to LO (active) for 5ms
    pulse_lo(WRITE, length=0.005)
    # OE to LO (active)
    off(READ)

    # Put the ports back to read and they should read the byte written
    for port in D_ports:
        GPIO.setup(port, GPIO.IN)

    if inc:
        incr()


def write_file(filename, start=0):
    """Write contents of binary file to location 'start'"""
    with open(filename, 'rb') as f:
        find(start)
        byte = f.read(1)
        num_bytes = 0
        while byte:
            write(ord(byte), inc=True)
            num_bytes += 1
            byte = f.read(1)
    return num_bytes

def cleanup():
    GPIO.cleanup()

def verify_file(filename, start=0):
    """Verify contents of binary file against memory from 'start'"""
    with open(filename, 'rb') as f:
        find(start)
        file_byte = f.read(1)
        num_bytes = 0
        while file_byte:
            chip_byte = read(type='dec', inc=True)
            if ord(chip_byte) != ord(file_byte):
                err_str = 'Verify error at byte %0X: chip=%0x file=%0x' % (start+num_bytes, ord(chip_byte), ord(file_byte))
                cleanup()
                raise Exception(err_str)
            num_bytes += 1
            file_byte = f.read(1)
    return num_bytes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Write file to EEPROM')
    parser.add_argument('filename', help='path to binary file to write')
    readwrite = parser.add_mutually_exclusive_group(required=True)
    readwrite.add_argument('--write', '-w', action='store_true', help='Write the file to location')
    readwrite.add_argument('--verify', '-r', action='store_true', help='Verify the file with location')
    parser.add_argument('--location', '-l', default='0', type=str, help='memory location to begin write: use 0x for hex or plain for decimal. Defaults to 0.')
    args = parser.parse_args()
    location = int(args.location, 0)
    length_string = "{0} ({0:04X}) bytes."
    if args.write:
        print "Writing file %s to location 0x%04X" % (args.filename, location)
        num_bytes = write_file(args.filename, location)
        print "Wrote " + length_string.format(num_bytes)
    print "Verifying location 0x%04X with file %s" % (location, args.filename)
    num_bytes = verify_file(args.filename, location)
    print "File verified OK: " + length_string.format(num_bytes)
    cleanup()
