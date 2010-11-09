import phm
p=phm.phm()

p.write_outputs(0)
p.set_pulse_width(13)
p.set_pulse_polarity(0)
p.enable_pulse_high(3)	# modify read block to send a pulse

for x in range(10):
  print p.pulse2rtime(3,3)

data = p.read_block(200,10,1)
p.plot(data)
p.save_data(data, 'piezo.dat')
raw_input()   # wait for key press