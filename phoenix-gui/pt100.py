from Tkinter import *
import Image, ImageTk, os, time, math
from utils import Data, abs_path

photograph = 'pt100.jpg'	# full path required 

class pt100:
    NP = 400
    delay = 0.03	# minimum delay between voltage reads
    tmax = 12.0		# Number of seconds for NP reads
    looping = False
    xlabel = 'Seconds'
    ylabel = 'Kelvin'
    gain = 11.0		# Assume PT100 output is amplified by 11
    ccval = 1.0		# CCS nominal value is 1 mA
    maxtemp = 800.0
    size = [100,100]
    del_scale = None    
    np_scale = None    
    
    def __init__(self, parent, size, plot, msg):
        self.parent = parent
        self.plot2d = plot
        self.msgwin = msg
        x = Image.open(abs_path(photograph))
        im = x.resize(size)
        self.size[0] = float(size[0])
        self.size[1] = float(size[1])
        self.image = ImageTk.PhotoImage(im)
        self.canvas = Canvas(parent, width = size[0], height = size[1])
        self.canvas.create_image(0,0,image = self.image, anchor = NW)
        self.data = Data()

    def enter(self, p):	
      self.ph = p 
      self.ph.select_adc(0)
      self.ph.set_adc_size(2)
      self.intro_msg()
      self.tmax = self.delay * self.NP
      self.plot2d.setWorld(0, 0, self.tmax, self.maxtemp)	
      self.plot2d.mark_axes(self.xlabel,self.ylabel)

    def exit(self):
      self.looping = False
      
    def set_delay(self,w):
        if self.looping:
          return
        d = self.del_scale.get()    
        self.delay = float(d)/1000.0
        self.plot2d.setWorld(0, 0, self.NP * self.delay, self.maxtemp)	
        self.plot2d.mark_axes(self.xlabel,self.ylabel)
        if len(self.data.points) < 2:
          return
        self.plot2d.delete_lines()
        self.plot2d.line(self.data.points, self.col)
        
    def set_NP(self,w):
        d = self.np_scale.get()    
        self.NP = d
        self.plot2d.setWorld(0, 0, self.NP * self.delay, self.maxtemp)	
        self.plot2d.mark_axes(self.xlabel,self.ylabel)
        if len(self.data.points) < 2:
          return
        self.plot2d.delete_lines()
        self.plot2d.line(self.data.points, self.col)
        
    def clear(self,e):
        self.plot2d.delete_lines()  
        self.data.clear()

    def save(self,e):
        fname = self.fntext.get()
        if fname == None:
          return
        self.data.save(fname)
        self.msgwin.msg('Data saved to '+ fname)

    def analyze(self,e):
        self.data.analyze(self.xlabel, self.ylabel)

    def save_all(self,e):
        fname = self.fntext.get()
        if fname == None:
          return
        self.data.save_all(fname)
        self.msgwin.msg('Data saved to '+ fname)

    def show_all(self,e):
        self.plot2d.delete_lines()  
        self.data.index = 0
        for tr in self.data.traces:
          self.plot2d.line(tr,self.data.get_col())
#------------------------------------------------------------------        
        
    def start(self,e):
        if self.ph == None:
            self.msgwin.msg('Connection not made yet', 'red')
            return
        if self.looping == False:    		# Same color if restarted
        	self.col = self.data.get_col()
        self.msgwin.msg('Started Temperature Recording')
	self.looping = True
	self.data.points = []
	
    def stop(self,e):
        self.msgwin.msg('Stopped Recording')
        self.accept_trace()
        self.looping = False

    def accept_trace(self):
        self.data.traces.append(self.data.points)

    def update(self):
        if self.looping == False:
            return
        if self.delay > 0:
          time.sleep(self.delay)
        val = self.ph.get_voltage()
        if self.data.points == []:
          self.start_time = val[0]
        temp = self.mv2cel(val[1])
        self.data.points.append( (val[0]-self.start_time, temp) )
        if len(self.data.points) < 2:
          return
        self.plot2d.delete_lines()
        self.plot2d.line(self.data.points, self.col)
        if len(self.data.points) >= self.NP:
          self.msgwin.msg('Temperature recording finished')
          self.accept_trace()
          self.looping = False

    def mv2cel(self,mv):
        self.offset = 0.0
	mv = (mv - self.offset)/self.gain
	r = mv / self.ccval
        # Convert resistance to temperature for PT100
	r0 = 100.0
	A = 3.9083e-3
	B = -5.7750e-7
	c = 1 - r/r0
	b4ac = math.sqrt( A*A - 4 * B * c)
	t = (-A + b4ac) / (2.0 * B)
	print t 
	return t + 273

    def calibrate(self,e):
        try:
          s = self.gaintext.get()
          self.gain = float(s)
          s = self.cctext.get()
          self.ccval = float(s)
        except:
          self.msgwin.msg('Error occured during calibration','red')

    def intro_msg(self):
        self.clear(None)
        self.msgwin.clear()
        self.msgwin.showtext('Resistance of the PT100 sensor is a function '+\
        'of temperature. The sonsor is connected to a 1mA constant current '+\
        'source an the voltage across the sensor is measured after '+\
        'sufficient amplification.')
        self.msgwin.showlink('Start', self.start)
        self.msgwin.showtext(' Start Recording Temperature')
        self.msgwin.showlink('Stop', self.stop)
        self.msgwin.showtext(' Stop Recording Temperature')

        self.msgwin.showlink('Save the latest trace', self.save)
        self.msgwin.showtext(' or ')
        self.msgwin.showlink('Save all Traces', self.save_all)
        self.msgwin.showtext(' to a file named ')
        self.fntext =  Entry(None, width =20, fg = 'red')
        self.msgwin.showwindow(self.fntext)
        self.fntext.insert(END,'pt100.dat')
        self.msgwin.showtext(' (You can change the filename)\n')

        self.msgwin.showlink('Analyze', self.analyze)
        self.msgwin.showtext(' Process the data using Xmgrace.\n')
        self.msgwin.showlink('Display all Traces', self.show_all)
        self.msgwin.showtext(' to see all the data collected and ')
        self.msgwin.showlink('Clear all Traces', self.clear)
        self.msgwin.showtext(' Clear Everything ')

        self.msgwin.showtext('\nSet Maximum Number of Readings')
        if self.np_scale != None:
            self.np_scale.destroy()
        self.np_scale =  Scale(None, command = self.set_NP, \
          from_ = 10, to=1000, orient=HORIZONTAL, length=100, showvalue = 1)
        self.np_scale.set(self.NP)
        self.msgwin.showwindow(self.np_scale)

        self.msgwin.showtext(' and the Interval between readings ')
        if self.del_scale != None:
            self.del_scale.destroy()
        self.del_scale =  Scale(None, command = self.set_delay, \
          from_ = 30, to=1000, orient=HORIZONTAL, length=100, showvalue=1)
        self.del_scale.set(self.delay)
        self.msgwin.showwindow(self.del_scale)
        self.msgwin.showtext(' milli seconds.\n')

        self.msgwin.showtext('For calibration enter the amplifier gain ')
        self.gaintext =  Entry(None, width =10, fg = 'red')
        self.msgwin.showwindow(self.gaintext)
        self.gaintext.insert(END,'11.0')
        self.msgwin.showtext(' and the CCS value')
        self.cctext =  Entry(None, width =10, fg = 'red')
        self.msgwin.showwindow(self.cctext)
        self.cctext.insert(END,'1.0')
        self.msgwin.showtext('mA and ')
        self.msgwin.showlink('Click Here\n', self.calibrate)
              
