import phm, time

def find_peaks(data):
    vmin = 5.0
    vmax = -5.0
    t1 = t2 = 0
    for p in data:
        if p[1] < vmin:
            vmin = p[1]
            t1 = p[0]
	if p[1] > vmax:
	    vmax = p[1]
	    t2 = p[0]
#    print vmin, vmax
    if t1 < t2:			# return left side peak first
        return (t1,vmin), (t2,vmax)
    else:
        return (t2,vmax),(t1,vmin)

NP = 400
delay = 250
maxtime = NP*delay

p=phm.phm()
p.select_adc(0)
p.set_adc_size(2)
print 'Conenct coil to CH0 through the level shifter and press Enter'
raw_input()
a = p.read_block(400,250,1)

peaks = find_peaks(a)
noise = peaks[0][1]

print 'Noise level = %5.0f mV'%noise
print 'Keep dropping the magnet until trace is captured'

while 1:
      a = p.read_block(400,250,1)
      p.plot_data(a)
      peaks = find_peaks(a)
      if abs(peaks[0][1] - noise) > 500:
          if peaks[0][0] > maxtime*0.1 and peaks[1][0] < maxtime*0.9:
              p.save_data(a, 'induction.dat')
              break
print 'Data Saved to "induction.dat". Press <Enter> key to exit'
raw_input()
