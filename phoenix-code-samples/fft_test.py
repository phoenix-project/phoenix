import phm, phmath
p=phm.phm()

data = p.read_block(800,20,1)
#p.plot(data) ; raw_input()
trans = phmath.fft(data)
size = len(trans)

xmin = trans[0][0]
xmax = trans[-1][0]
ymin = 0.0
ymax = 0.0
for k in range(size):
    if trans[k][1] > ymax: ymax = trans[k][1]
    if trans[k][1] < ymin: ymin = trans[k][1]

print xmin,ymin,xmax,ymax

p.plot(trans)
p.set_scale(xmin,ymin,xmax,ymax*1.1)
raw_input()

