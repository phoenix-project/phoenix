"""data was taken with 1K resistor, 1uF capacitor
Three sets are taken:

a) freq=1000 Hz and sampling delay = 10micro seconds, samples=400
b) freq=5000 Hz and sampling delay = 10micro seconds, samples=300
c) freq=100 Hz  sampling delay = 20micro seconds, samples=300
"""

import phm
p = phm.phm()
freq = 1000
samples = 200
delay = 10
p.add_channel(0)
p.add_channel(1)
print p.set_frequency(freq)
print 'Ground any Digital Input to Exit...'
while p.read_inputs() == 15:
	p.plot_data(p.multi_read_block(samples, delay,0))
