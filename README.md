# Raspberry-Pi-EEPROM-writer
Python module to use a Raspberry Pi to read/write to EEPROM

This Python module will control a Raspberry Pi such that it drives a circuit to read and write to a parallel EEPROM such as a CAT28C65B or similar (13 address lines, 8 data lines, chip enable, output enable, write enable).

The circuit required is three chained counter chips to hold a 12-bit address on A0-A11 (tie A12 low (or high if you want to write to the upper half)) with a single increment line, plus a reset line.

Run on the Pi with ``sudo python eeprom.py --help``

Or use interactively in a Python shell:
```
from writer import *
find(0)
dump()
```

Raspberry Pi Pins
-----------------
`incr` is the increment line to the counter chips
`reset` is the counter chips' reset line
`led` can control an LED
The other connections are on the EEPROM chip
The colours are for my tracking

wire | Pi pin | port | purpose
--- | --- | --- | ---
red | 2 | 5V
brown | 6 | GND
orange | 3 | GPIO2 | incr
yellow | 5 | GPIO3 | reset
green | 7 | GPIO4 | WRITE
black1 | 11 | GPIO17 | READ
white1 | 13 | GPIO27 | D0
grey1 | 15 | GPIO22 | D1
blue1 | 12 | GPIO18 | D2
purple1 | 16 | GPIO23 | D3
purple2 | 24 | GPIO8 | D4
blue2 | 26 | GPIO7 | D5
grey2 | 23 | GPIO11 | D6
white2 | 21 | GPIO9 | D7
black2 | 19 | GPIO10 | led
