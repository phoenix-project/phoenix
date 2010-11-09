# Connect the applied and induced signals to CH1 and CH0. DAC can make a
# sinewave but an external one is much better.

import phm, time, math
p=phm.phm()

def set_sine():
  v = []
  for i in range(100):
      x = 127.5 + 127.5 * math.sin(2.0*math.pi*i/100)
      x = int(x+0.5)
      v.append(x)
  p.load_wavetable(v)	
  res = p.start_wave(50)

set_sine()		# Comment this line for external sine wave
p.set_adc_size(2)
p.add_channel(0)
p.add_channel(1)

print 'Connect any digital input to GND to stop'
while p.read_inputs() ==  15:
    data = p.multi_read_block(100,200,1)
    p.plot_data(data)
    
p.stop_wave()
print 'Saving data to file'
p.save_data(data, 'mu_induction.dat')

