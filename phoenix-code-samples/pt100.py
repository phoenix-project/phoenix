import phm, math, time
p = phm.phm()

gain = 30.7		# amplifier gain
offset = 0.0		# Amplifier offset, measured with input grounded
ccs_current = 1.0	# CCS output 1 mA

def r2t(r):	# Convert resistance to temperature for PT100
	r0 = 100.0
	A = 3.9083e-3
	B = -5.7750e-7
	c = 1 - r/r0
	b4ac = math.sqrt( A*A - 4 * B * c)
	t = (-A + b4ac) / (2.0 * B)
	return t

def v2r(v):
	v = (v + offset)/gain
	return v / ccs_current


p.select_adc(0)
p.set_adc_size(2)

print 'Data is also written to the file pt100.dat'
of = open('pt100.dat','w')

strt = p.zero_to_5000()[0]
for x in range(100):
	res = p.zero_to_5000()
	r = v2r(res[1])
	temp = r2t(r)
	ss = '%5.2f %5.2f' %(res[0]-strt, temp)
	of.write(ss+'\n')
	print ss
	time.sleep(1.0)
