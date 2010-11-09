# Connect the electromagnet from Digital Output D0 to GND.
# Loudspeaker between GND and Digital Input D0
import phm, time
p=phm.phm()

p.write_outputs(1)
print 'Attach the Iron Ball...'
time.sleep(3)
print p.clr2rtime(0,0)
