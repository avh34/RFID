################################################################################
#                                                                              #
# @file:   MFRC522_SPI.py                                                      #
#                                                                              #
# @author: Andre Heil <andre.v.heil@gmail.com>                                 #
#                                                                              #
# @date:   May 4th 2016                                                        #
#                                                                              #
# @brief:  This module should handle the MFRC522's SPI interface and abstract  #
#          it away from the rest of the application                            #
#                                                                              #
################################################################################

import spidev


class MFRC522_SPI:

    def __init__( self ):
        self.spi = spidev.SpiDev()
        self.spi.open( 0, 0 )


    def write( self, reg, value ):
        self.spi.xfer([(reg << 1) & 0x7E, value])


    def read ( self, reg ):
        return self.spi.xfer([((reg << 1) & 0x7E) | 0x80, 0x00])[1]


    def set_bits( self, reg, mask ):
        current = self.read( reg )
        self.write( reg, current |  mask )


    def clr_bits( self, reg, mask ):
        current = self.read( reg )
        self.write( reg, current & ~mask )