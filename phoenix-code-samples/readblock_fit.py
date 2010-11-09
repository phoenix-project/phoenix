import phm, time, phmath

p = phm.phm()

of = open('vf.dat','w')
for k in range(0,256,5):
    p.set_dac(k)
    time.sleep(0.1)
    data = p.read_block(400,100,0)
    res = phmath.fit_sine(data)
    frfit = res[1][1]*1.0e6
    if frfit < 90:
        print frfit
        continue
#        p.plot(res[0]);raw_input()
    ss = '%5.0f %4.1f'%(k*5000.0/255, frfit)
    print ss
    of.write(ss+'\n')
    of.flush()
    