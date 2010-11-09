import phm, phmath
p=phm.phm()

ifp=open('cap.dat','r')

data = []
while 1:
  a = ifp.readline()
  if a == '': break
  ss = a.split()
  data.append( [float(ss[0]), float(ss[1])])
 
res = phmath.fit_exp(data)
frfit = res[1][1]*1.0e6
print frfit

p.plot(res[0])
p.set_scale(0,0,5,5)
raw_input()
