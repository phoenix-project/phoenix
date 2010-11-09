"""
Connect Capacitor between CH0 and GND. Resistor from D3out to CH0.
For linear charging:
Connect capcitor between D3out and CH0. Resistor from CCS to CH0
"""

import phm, time
p=phm.phm()

p.select_adc(0)
p.set_adc_size(2)
p.write_outputs(8)
time.sleep(1)
p.enable_set_low(3)
v=p.read_block(200,25,0)
p.plot_data(v)
p.save_data(v, 'cap.dat')
print 'Press any Key to Exit'
raw_input()
