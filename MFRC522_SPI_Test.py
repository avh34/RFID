import os
import sys

import MFRC522_Registers as reg
import MFRC522_SPI

spi = MFRC522_SPI.MFRC522_SPI()

spi.write( reg.T_MODE,       0x8D )
spi.write( reg.T_PRESCALER,  0x3E )
spi.write( reg.T_RELOAD_L,   0x1E )
spi.write( reg.T_RELOAD_H,   0x00 )
spi.write( reg.TX_ASK,       0x40 )
spi.write( reg.MODE,         0x3D )
spi.write( reg.T_MODE,       0x78 )
spi.write( reg.RX_THRESHOLD, 0x11 )

while True:
    reg  = raw_input("Reg:  ")
    data = raw_input("Data: ")

    reg  = int( reg,  16 )
    data = int( data, 16 )

    spi.write( reg, data )
    print "Reg 0x" + format( reg, '02x' ) + " = 0x" + format ( spi.read( reg ), '02x' )