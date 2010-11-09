import phm, time
p=phm.phm()

p.set_adc_size(2)
p.set_adc_delay(200)

va = 0.0
while va <= 5000.0:
  p.set_voltage(va)
  time.sleep(0.001)
  vb = p.zero_to_5000()[1]
  va = va + 19.6
  print vb, ' ' , (va-vb)/1000.0
  
