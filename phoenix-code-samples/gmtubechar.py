"""
Generate data for GM tube characteristic. Change TIME depending on the
strength of the source used
"""
TIME = 1		# 1 second

import phm, time
p=phm.phm()

of = open('gm.dat','w')

for v in range(100,901,50):
    tv = p.gm_set_voltage(v)
    c = p.gm_get_count(TIME)
    ss = '%4.0f %d'%(tv,c)
    of.write(ss+'\n')
    of.flush()
    print ss
p.set_voltage(0)
