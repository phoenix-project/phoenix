import phm, time 

p=phm.phm()
p.set_frequency(10) 
p.clear_hist()
p.start_hist()
print 'waiting..'
time.sleep(1)
print 'done'
p.stop_hist()
v = p.read_hist()
f = open('hist.dat','w')
for k in v: 
    if k[1] != 0:
      print k
    ss = '%d %d\n'%(k[0], k[1] )
    f.write(ss)