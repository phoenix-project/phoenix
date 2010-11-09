"""
Reads a waveform from CH0, plots the wave and it Fast Fourier Transform. Used with Analog Box.
Connect the GND of Phoenix and Analog Box. Connect SG1 out to AM input of SG2. 
Connect SG2 output to CH) through a level shifter. 
"""
import phm, phmath
p=phm.phm()

p.select_adc(0)
p.set_adc_size(1)
data = p.read_block(800,40,1) 
p.save_data(data,'amwave.dat')
res = phmath.fft(data)
p.save_data(res,'amfft.dat')
p.plot(res)			
p.auto_scale(res)
raw_input()			# wait for a Keypress
