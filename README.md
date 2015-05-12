# Raspberry-Pi-EEPROM-writer
Python module to use a Raspberry Pi to read/write to EEPROM

This Python module will control a Raspberry Pi such that it drives a circuit to read and write to a parallel EEPROM such as a CAT28C65B or similar (13 address lines, 8 data lines, chip enable, output enable, write enable).

The circuit required is essentially a set of counter chips to hold an address chained (with a single increment line), plus a reset line.
