import phm, phmath
p=phm.phm()


def make_hist(y, nb):
    min = 1.0e10
    max = 0
    for k in y:
        if k > max: max = k
        if k < min: min = k
    span = max - min
    high = max + span
    low  = min - span
    hist = [0] * nb
    for k in y:
       i = int((k - low)/(high-low)*nb)
       hist[i] = hist[i] + 1
#       print k, low, k-low, (k-low)/nb, i
    return hist
    print hist
    print low, min, max, high, span

p.set_adc_size(2)
p.set_frequency(500)
res = []
for k in range(100):
    t = p.r2ftime(0,0)
#    t = p.get_voltage()[1]
#    print t
    if t > 0:
        res.append(float(t))

hist = make_hist(res,7)
data = []
for k in range(len(hist)):
    data.append([k,hist[k]])
p.plot(data)
fit = phmath.fit_gauss(data)
p.plot(fit[0])
print fit[1] 
p.set_scale(0, 0, 10, 100)
raw_input()       