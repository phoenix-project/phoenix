import phm
p=phm.phm()

pos = 0
seq = [12, 6, 3, 9]

def rotate (nsteps, dir=0):
	global pos, seq
	for i in range(nsteps):
		if dir == 1:       # clockwise
			if pos == 3:
				pos = 0
			else:
				pos = pos + 1
		else:
			if pos == 0:
				pos = 3
			else:
				pos = pos-1
		p.set_port(0,seq[pos])
		
p.set_ddr(0,15)
rotate(100,1)
rotate(100,0)

