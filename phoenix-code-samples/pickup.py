import phm
p = phm.phm()

p.select_adc(0)
print 'Ground any Digital Input to Save data and Exit..'
while p.read_inputs() == 15:
    v = p.read_block(200, 500,1)
    p.plot_data(v)
p.save_data(v, 'pickup.dat')