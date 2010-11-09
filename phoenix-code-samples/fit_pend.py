import phm, phmath
p=phm.phm()

ifp=open('pend.dat','r')

data = []
while 1:
  a = ifp.readline()
  if len(a) < 3: break
  ss = a.split()
  data.append( [float(ss[0]), float(ss[1])])

res = phmath.fit_dsine(data)
frfit = res[1][1]*1.0e6
print frfit

p.plot(res[0])
p.save_data(res[0])
p.set_scale(0,-5,5,5)
raw_input()
