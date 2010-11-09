# Connect the DC motor to CH0 through amplifier (gain = 100) and level shifter.
import phm, time
p=phm.phm()

f = open('pendulum.dat','w')

p.select_adc(0)
p.set_adc_size(2)

start = p.get_voltage_bip()[0]
while 1:
    res = p.get_voltage_bip()
    tm = res[0] - start			# elapsed time
    ss = '%6.3f %6.0f'%(tm,res[1])
    print ss
    f.write(ss+'\n')
    if tm > 5:
      break
