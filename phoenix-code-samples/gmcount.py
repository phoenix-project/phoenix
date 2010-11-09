#Count the GM tune output for one second , ten times. 
import phm, time
p=phm.phm()

TIME = 1
print 'Tube voltage = ',p.gm_set_voltage(500)

of = open('gm.dat','w')
for x in range(10):
     fr = p.gm_get_count(TIME)
     of.write(str(fr))
     of.write('\n')
     print fr
     