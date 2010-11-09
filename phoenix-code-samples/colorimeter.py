import phm, time, math
from Tkinter import *

MAXLIGHT = 4800.0	# maximum output expected from light sensor
led_drive = 0.0
light_output = 1.0
calibrated = False

def set_fullscale():
  global light_output, led_drive, calibrated
  Light.configure(text = 'Calibrating..')
  Light.update()
  led = 2000.0
  while led < 5000:
      p.set_voltage(led)
      time.sleep(0.1)
      light = p.get_voltage()[1]
#      print led, light
      if light > MAXLIGHT:
          led_drive = led
          light_output = light
          s = 'Light = %4.1f at Drive = %4.1f'%(light,led)
          Light.configure(text=s)
          calibrated = True
          return
      led = led + 5000.0/255
      
def read_light():
    global calibrated
    if calibrated == False:
        s = 'Calibrate first'
    else:
        light = p.get_voltage()[1]
        s = '%4.1f%% of light tranmitted'%(light/light_output*100)
    Light.config(text = s)
    
p=phm.phm()
p.select_adc(0)
p.set_adc_size(2)
p.set_adc_delay(200)

w = Tk()
f = Frame(w)
f.pack()
Calib = Button(f,text = 'Calibrate', command = set_fullscale)
Calib.pack(side=LEFT)
Read = Button(f,text = 'Transmittance', command = read_light)
Read.pack()

Light = Label(w,text = '0.0', width = 40)
Light.pack()
w.title('Colorimeter')
w.mainloop()
 