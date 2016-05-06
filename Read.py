import MFRC522
import signal
import time

run = True
rdr = MFRC522.MFRC522()
util = rdr.util()
util.debug = True

def end_read(signal,frame):
    global run
    print "\nCtrl+C captured, ending read."
    run = False
    rdr.cleanup()

signal.signal( signal.SIGINT, end_read )

print "Starting"
while run:
    (error, data) = rdr.request()
    if not error:
        print "Hit: " + str( data )

    (error, uid) = rdr.anticoll()
    if not error:
        print "UID: " + str( uid )

        #print "Setting tag"
        #util.set_tag(uid)
        #print "\nAuthorizing"
        #util.auth(rdr.auth_a, [0x12, 0x34, 0x56, 0x78, 0x96, 0x92])
        #util.auth(rdr.auth_b, [0x74, 0x00, 0x52, 0x35, 0x00, 0xFF])
        #print "\nReading"
        #util.read_out(4)
        #print "\nDeauthorizing"
        #util.deauth()
        
        #time.sleep(1)