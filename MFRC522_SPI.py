"""MFRC522 SPI Interface

This module is meant to abstract the SPI interface. The MFRC522 module uses this
module to perform its SPI communications with the MFRC522 chip.

This module is implemented as a class. We initialize a spidev object on which we
use to perform the transfer of data. The specifics of SPI communication with the
MFRC522 chip can be in section 8.1.2 (page 10) of the MFRC522 data sheet. It
explains the data format of reads and writes made to the MFRC522.

"""

#===============================================================================
# Imports
#===============================================================================

import spidev


#===============================================================================
# MFRC522 SPI Interface Class
#===============================================================================

class MFRC522_SPI:

    def __init__(self, bus, device):
        """Creates a spidev object and opens it on given bus and device"""
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)


    def read(self, reg):
        """Performs the read operation for the MFRC522

        This function follows the specification provided by section 8.1.2.1
        (page 10) of the MFRC522 data sheet.
        """
        return self.spi.xfer([((reg << 1) & 0x7E) | 0x80, 0x00])[1]


    def write(self, reg, value):
        """Performs the write operation for the MFRC522

        This function follows the specification provided by section 8.1.2.2
        (page 11) of the MFRC522 data sheet.
        """
        self.spi.xfer([(reg << 1) & 0x7E, value])


    def set_bits(self, reg, mask):
        """Sets the bits in mask to the given register"""
        current = self.read(reg)
        self.write(reg, current | mask)


    def clr_bits(self, reg, mask):
        """Clears the bits in mask to the given register"""
        current = self.read(reg)
        self.write(reg, current & ~mask)
