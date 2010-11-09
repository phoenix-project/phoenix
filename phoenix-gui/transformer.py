from Tkinter import *
import Image, ImageTk, math, os
import phm, time
from utils import Data, abs_path

photograph = 'trans.jpg'

class tran:
    NP = 200
    adc_delay = 250
    numchans = 2
    xlabel = 'milli seconds'
    ylabel = 'Volts'
    size = [350.0, 272.0]

    def __init__(self, parent, size, plot, msg):
        self.parent = parent
        self.plot2d = plot
        self.msgwin = msg
        x = Image.open(abs_path(photograph))
        im = x.resize(size)        

        self.size[0] = float(im.size[0])
        self.size[1] = float(im.size[1])
        self.image = ImageTk.PhotoImage(im)
        self.canvas = Canvas(parent, width = im.size[0], height = im.size[1])
        self.canvas.create_image(0,0,image = self.image, anchor = NW)
        self.data = Data()

    def enter(self, fd):
        self.ph = fd
        self.ph.set_adc_delay(self.adc_delay)
        self.plot2d.setWorld(0, -5, self.NP * self.adc_delay/1000.0, 5)
        self.plot2d.mark_axes(self.xlabel, self.ylabel, self.numchans)
        
        self.ph.add_channel(0)
        self.ph.add_channel(1)
        self.ph.del_channel(2)
        self.ph.del_channel(3)

        self.msg_intro()
	v = []
        for i in range(100):
	    x = 127.5 + 127.5 * math.sin(2.0*math.pi*i/100)
	    x = int(x+0.5)
	    v.append(x)
	self.ph.load_wavetable(v)	
	res = self.ph.start_wave(20)
	s = 'DAC is set to generate %3.1f Hz Sine Wave'%(res)
	self.msgwin.msg(s)
        self.updating = True

    def exit(self):
       self.updating = False
       self.ph.stop_wave()
       for k in range(4):
           self.ph.del_channel(k)

#--------------------------------------------------------------------

    def update(self):
        if self.ph == None:
            return
        phdata = self.ph.multi_read_block(self.NP, self.adc_delay, 0)
        if phdata == None:
            return

        self.data.points = []
        self.data.points2 = []
        for pt in phdata:
            self.data.points.append( (pt[0]/1000.0, 5.0 - 2.0 * pt[1]/1000.0) )
            self.data.points2.append((pt[0]/1000.0, 5.0 - 2.0 * pt[2]/1000.0) )
        self.plot2d.delete_lines()
        self.plot2d.line(self.data.points, 'black')
        self.plot2d.line(self.data.points2, 'red')

    def save_all(self,e):
        fname = self.fntext.get()
        if fname == None:
          return
        self.data.traces = []
        self.data.traces.append(self.data.points)
        self.data.traces.append(self.data.points2)
        self.data.save_all(fname)
        self.msgwin.msg('Data saved to '+ fname)
          
#-------------------------- Message routines -------------
    def msg_intro(self):
        self.msgwin.clear()
        self.msgwin.showtext('In this experiment, the DAC socket (producing '+\
        'a 50 Hz signal) is connected one end of a coil (Other end to GND) '+\
        'through a series capacitor. The same is also connected to CH1 via '+\
        'a level shifter for monitoring the primary waveform. '+\
        'Another coil (Secondary) is connected between Ground '+\
        'and the input of another level shifter, and its output '+\
        'is connected to CH0. Now you should see the primary waveform '+\
        'as a sinewave and the secondary as a horizontal line. Keep the '+\
        'coils close and note changes in secondary waveform. Pack them '+\
        'with ferrite core to see the effect of increased magnetic coupling\n')
        self.msgwin.showlink('Save Traces', self.save_all)
        self.msgwin.showtext('  Saves both the voltage waveforms to text file named ') 
        self.fntext =  Entry(None, width =20, fg = 'red')
        self.msgwin.showwindow(self.fntext)
        self.fntext.insert(END,'trans.dat')
        self.msgwin.showtext('\n\nTry changing the orientation of the coils, removing the ferrite '+\
        'etc. to study the effect of them')
