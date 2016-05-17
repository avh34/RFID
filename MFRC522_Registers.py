################################################################################
#                                                                              #
# @file:   MFRC522_Registers.py                                                #
#                                                                              #
# @author: Andre Heil <andre.v.heil@gmail.com>                                 #
#                                                                              #
# @date:   May 4th 2016                                                        #
#                                                                              #
# @brief:  This module is just a list of constants to make reading and writing #
#          to the MFRC522 chip easier and more readable.                       #
#                                                                              #
################################################################################


## Command and Status Registers ################################################
RESERVED_00     = 0x00
COMMAND         = 0x01
COM_I_EN        = 0x02
DIV_I_EN        = 0x03
COM_IRQ         = 0x04
DIV_IRQ         = 0x05
ERROR           = 0x06
STATUS_1        = 0x07
STATUS_2        = 0x08
FIFO_DATA       = 0x09
FIFO_LEVEL      = 0x0A
WATER_LEVEL     = 0x0B
CONTROL         = 0x0C
BIT_FRAMING     = 0x0D
COLL            = 0x0E
RESERVED_0F     = 0x0F


## Communication Registers #####################################################
RESERVED_10     = 0x10
MODE            = 0x11
TX_MODE         = 0x12
RX_MODE         = 0x13
TX_CONTROL      = 0x14
TX_ASK          = 0x15
TX_SEL          = 0x16
RX_SEL          = 0x17
RX_THRESHOLD    = 0x18
DEMOD           = 0x19
RESERVED_1A     = 0x1A
RESERVED_1B     = 0x1B
MF_TX           = 0x1C
MF_RX           = 0x1D
RESERVED_1E     = 0x1E
SERIAL_SPEED    = 0x1F


## Configuration Registers #####################################################
RESERVED_20     = 0x20
CRC_RESULT_H    = 0x21
CRC_RESULT_L    = 0x22
RESERVED_23     = 0x23
MOD_WIDTH       = 0x24
RESERVED_25     = 0x25
RF_CFG          = 0x26
GSN             = 0x27
CW_GSP          = 0x28
MOD_GSP         = 0x29
T_MODE          = 0x2A
T_PRESCALER     = 0x2B
T_RELOAD_H      = 0x2C
T_RELOAD_L      = 0x2D
T_COUNTER_VAL_H = 0x2E
T_COUNTER_VAL_L = 0x2F


## Test Registers ##############################################################
RESERVED_30     = 0x30
TEST_SEL_1      = 0x31
TEST_SEL_2      = 0x32
TEST_PIN_EN     = 0x33
TEST_PIN_VALUE  = 0x34
TEST_BUS        = 0x35
AUTO_TEST       = 0x36
VERSION         = 0x37
ANALOG_TEST     = 0x38
TEST_DAC_1      = 0x39
TEST_DAC_2      = 0x3A
TEST_ADC        = 0x3B
RESERVED_3C     = 0x3C
RESERVED_3D     = 0x3D
RESERVED_3E     = 0x3E
RESERVED_3F     = 0x3F