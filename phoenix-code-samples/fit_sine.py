import phm, phmath
p=phm.phm()

ifp=open('cro.dat','r')

data = []
while 1:
  a = ifp.readline()
  if a == '': break
  ss = a.split()
  data.append( [float(ss[0]), float(ss[1])])
 
res = phmath.fit_sine(data)
frfit = res[1][1]*1.0e6
print frfit

p.plot(res[0])
p.set_scale(0,-5,1,5)
raw_input()
