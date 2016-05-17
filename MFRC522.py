import RPi.GPIO as GPIO

import MFRC522_Registers as reg
import MFRC522_SPI       as spi

import signal

class Timeout():
    """Timeout class using ALARM signal."""
    class Timeout(Exception):
        pass

    def __init__(self, sec):
        self.sec = sec

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.sec)

    def __exit__(self, *args):
        signal.alarm(0)    # disable alarm

    def raise_timeout(self, *args):
        raise Timeout.Timeout()


IRQ_TX       = 0b01000000
IRQ_RX       = 0b00100000
IRQ_IDLE     = 0b00010000
IRQ_HI_ALERT = 0b00001000
IRQ_LO_ALERT = 0b00000100
IRQ_ERR      = 0b00000010
IRQ_TIMER    = 0b00000001

class MFRC522:
    pin_rst = 22

    # PCD  = Proximity coupling device         ( the reader )
    # PICC = Proximity integrated circuit card ( the tag    )

    PCD_IDLE       = 0x00
    PCD_AUTH       = 0x0E
    PCD_RECEIVE    = 0x08
    PCD_TRANSMIT   = 0x04
    PCD_TRANSCEIVE = 0x0C
    PCD_RESET      = 0x0F
    PCD_CRC        = 0x03

    auth_a = 0x60
    auth_b = 0x61

    act_read = 0x30
    act_write = 0xA0
    act_increment = 0xC1
    act_decrement = 0xC0
    act_restore = 0xC2
    act_transfer = 0xB0

    act_reqidl = 0x26
    act_reqall = 0x52
    act_anticl = 0x93
    act_select = 0x93
    act_end = 0x50

    reg_tx_control = 0x14
    length = 16

    authed = False

    def __init__( self, pin_rst = 22 ):
        self.pin_rst = pin_rst

        self.spi = spi.MFRC522_SPI(0, 0)

        GPIO.setmode( GPIO.BOARD        )
        GPIO.setup  ( pin_rst, GPIO.OUT )
        GPIO.output ( pin_rst,        1 )

        self.reset()

        self.spi.write( reg.T_MODE,       0x82 )
        self.spi.write( reg.T_PRESCALER,  0xA6 )
        self.spi.write( reg.T_RELOAD_L,   0x0A )
        self.spi.write( reg.T_RELOAD_H,   0x00 )

        self.spi.write( reg.TX_ASK,       0x40 )
        #self.spi.write( reg.MODE,         0x20 )
        self.spi.write( reg.RX_THRESHOLD, 0x11 )
        #self.spi.clr_bits( reg.RX_MODE,   0x04 )

        self.set_antenna( True )


    def set_antenna( self, state ):
        if state == True:
            current = self.spi.read( reg.TX_CONTROL )
            if ~(current & 0x03):
                self.spi.set_bits(reg.TX_CONTROL, 0x03)
        else:
            self.spi.clr_bits(reg.TX_CONTROL, 0x03)


    def authenticate( self, block_addr, key, ser_num ):

        irq_wait = IRQ_IDLE | IRQ_RX | IRQ_TIMER

        self.spi.write   ( reg.COMMAND, self.PCD_IDLE )
        self.spi.clr_bits( reg.COM_IRQ,          0x80 )
        self.spi.set_bits( reg.FIFO_LEVEL,       0x80 )

        data = [0x60] + block_addr + key + ser_num
        for datum in data:
            self.spi.write(reg.FIFO_DATA, datum)

        self.spi.write(reg.COMMAND, self.PCD_AUTH)

        irq = 0x00
        while not (irq & irq_wait):
            irq = self.spi.read(reg.COM_IRQ)

        if irq & IRQ_TIMER:
            return True


    def card_write( self,  data ):
        back_data = []
        back_len  = 0
        error     = False

        irq_wait = IRQ_IDLE | IRQ_RX | IRQ_TIMER

        self.spi.clr_bits( reg.COM_IRQ,             0x80 )
        self.spi.set_bits( reg.FIFO_LEVEL,          0x80 )

        for datum in data:
            self.spi.write( reg.FIFO_DATA, datum )

        self.spi.write   ( reg.COMMAND,     self.PCD_TRANSCEIVE )
        self.spi.set_bits( reg.BIT_FRAMING, 0x80                )

        irq = 0x00
        while not ( irq & irq_wait ):
            irq = self.spi.read( reg.COM_IRQ )

        self.spi.write(reg.COMMAND, self.PCD_IDLE)

        if irq & IRQ_TIMER:
            return True, back_data, back_len

        if self.spi.read( reg.ERROR ):
            return True, back_data, back_len

        byte_num  = self.spi.read( reg.FIFO_LEVEL )
        last_bits = self.spi.read( reg.CONTROL    ) & 0x07
        if last_bits is 0x00:
            back_len = byte_num * 8
        else:
            back_len = ( byte_num - 1 ) * 8 + last_bits

        byte_num = min( self.length, byte_num )

        for i in range( byte_num ):
            back_data.append(self.spi.read(reg.FIFO_DATA))

        return error, back_data, back_len


    def request(self, req_mode=0x26):

        self.spi.write( reg.BIT_FRAMING, 0x07 )

        (error, back_data, back_bits) = self.card_write( [req_mode] )

        if error or (back_bits != 0x10):
            return True, None

        return False, back_data


    def anticoll(self):
        """
        Anti-collision detection.
        Returns tuple of (error state, tag ID).
        """
        serial_number = []

        serial_number_check = 0
        
        self.spi.write( reg.BIT_FRAMING, 0x00)
        serial_number.append(self.act_anticl)
        serial_number.append(0x20)

        (error, back_data, back_bits) = self.card_write(serial_number)
        if not error:
            if len(back_data) == 5:
                for i in range(4):
                    serial_number_check = serial_number_check ^ back_data[i]

                if serial_number_check != back_data[4]:
                    error = True
            else:
                error = True
        
        return (error, back_data)


    def calculate_crc(self, data):
        self.spi.clr_bits( reg.DIV_IRQ,    0x04 )
        self.spi.set_bits( reg.FIFO_LEVEL, 0x80 )

        for i in range( len( data ) ):
            self.spi.write( reg.FIFO_DATA, data[i] )
        self.spi.write(reg.COMMAND, self.PCD_CRC)

        i = 255
        while True:
            n = self.spi.read(reg.DIV_IRQ)
            i -= 1
            if not ((i != 0) and not (n & 0x04)):
                break

        ret_data = [self.spi.read( reg.CRC_RESULT_L ),
                    self.spi.read( reg.CRC_RESULT_H )]

        return ret_data

    def select_tag(self, uid):
        """
        Selects tag for further usage.
        uid -- list or tuple with four bytes tag ID
        Returns error state.
        """
        back_data = []
        buf = []

        buf.append(self.act_select)
        buf.append(0x70)

        for i in range(5):
            buf.append(uid[i])

        crc = self.calculate_crc(buf)
        buf.append(crc[0])
        buf.append(crc[1])

        (error, back_data, back_length) = self.card_write( buf )

        if (not error) and (back_length == 0x18):
            return False
        else:
            return True


    def card_auth(self, auth_mode, block_address, key, uid):
        """
        Authenticates to use specified block address. Tag must be selected using
        select_tag(uid) before auth.
        auth_mode -- RFID.auth_a or RFID.auth_b
        key -- list or tuple with six bytes key
        uid -- list or tuple with four bytes tag ID
        Returns error state.
        """


        #buf = []
        #buf.append( auth_mode )
        #buf.append( block_address )

        #for i in range( len( key ) ):
        #    buf.append(key[i])

        #for i in range(4):
        #    buf.append(uid[i])

        #( error, back_data, back_length ) = self.card_write(self.PCD_AUTH, buf)
        #if not ( self.spi.read( reg.STATUS_2 ) & 0x08 ) != 0:
        #    error = True

        #if not error:
        #    self.authed = True

        #return error

        pass

    def stop_crypto( self ):
        """Ends operations with Crypto1 usage."""
        self.spi.clr_bits( reg.STATUS_2, 0x08 )
        self.authed = False


    def read( self, block_address ):
        """
        Reads data from block. You should be authenticated before calling read.
        Returns tuple of (error state, read data).
        """
        buf = [self.act_read, block_address]
        crc = self.calculate_crc(buf)
        buf.append( crc[0] )
        buf.append( crc[1] )
        (error, back_data, back_length) = self.card_write( buf )

        if len(back_data) != 16:
            error = True

        return error, back_data
   

    def write(self, block_address, data):
        """
        Writes data to block. You should be authenticated before calling write.
        Returns error state.
        """
        buf = [self.act_write, block_address]

        crc = self.calculate_crc(buf)
        buf.append(crc[0])
        buf.append(crc[1])

        (error, back_data, back_length) = self.card_write(self.PCD_TRANSCEIVE, buf)
        if not(back_length == 4) or not((back_data[0] & 0x0F) == 0x0A):
            error = True

        if not error:
            buf_w = []
            for i in range(16):
                buf_w.append(data[i])
               
            crc = self.calculate_crc(buf_w)
            buf_w.append(crc[0])
            buf_w.append(crc[1])
            (error, back_data, back_length) = self.card_write(self.PCD_TRANSCEIVE, buf_w)
            if not(back_length == 4) or not((back_data[0] & 0x0F) == 0x0A):
                error = True

        return error


    def reset( self ):
        self.spi.write(reg.COMMAND, self.PCD_RESET)


    def cleanup( self ):
        """
        Calls stop_crypto() if needed and cleanups GPIO.
        """
        if self.authed:
            self.stop_crypto()
        GPIO.cleanup()


    def util( self ):
        """
        Creates and returns RFIDUtil object for this RFID instance.
        If module is not present, returns None.
        """
        try:
            import RFIDUtil
            return RFIDUtil.RFIDUtil(self)
        except ImportError:
            return None