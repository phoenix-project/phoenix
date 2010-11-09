import phmath, phm
import scipy

p=phm.phm()
amplitude = 15
mean = 10
sigma = 0.5
NP = 200

par = [amplitude, mean, sigma]
deviation = scipy.rand(NP)/1.0
x = scipy.linspace(mean-10*sigma, mean +10*sigma, 200)
y = phmath.gauss_eval(x,par) + deviation

data = []
for k in range(NP):
  data.append( [x[k], y[k]])

res = phmath.fit_gauss(data)
print par, res[1]

p.plot(res[0])
p.set_scale(0, 0, mean*2, amplitude*1.2)
raw_input()
