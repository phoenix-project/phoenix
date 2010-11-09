import phm, time
p=phm.phm()

scale_factor = (2 * 5.6 + 0.056)/0.056/1000. # Potential divider 56K and 11.2M
a = 1
for dac in range(5,127):
    p.set_dac(dac)
    time.sleep(0.2)
    ss = '(%4.0f, %d),'%(p.get_voltage()[1]*scale_factor, float(dac))
    print ss,
    if (a % 6) == 0: print 
    a = a + 1
p.set_voltage(0)