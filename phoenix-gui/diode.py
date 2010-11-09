from Tkinter import *
import Image, ImageTk, os, time

from utils import Data, abs_path

photograph = 'diode_iv.jpg'		# full path required 

class diode:
    NP = 500
    looping = False
    xlabel = 'Volts'
    ylabel = 'mA'
    size = [100,100]
    dac_voltage = 0.0
    adc_voltage = 0.0
    step = 39.0
    
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
      self.plot2d.setWorld(0, 0, 5, 5)
      self.plot2d.mark_axes(self.xlabel, self.ylabel)
      self.intro_msg()

    def exit(self):
      self.looping = False

    def clear(self,e):
        self.data.clear()
        self.plot2d.delete_lines()  
              
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
        if self.looping == False:    # Same color if restarted in between
        	self.col = self.data.get_col()
        self.msgwin.msg('Starting Diode IV measurement')
        self.data.points = []
	self.looping = True
	self.dac_voltage = 0.0
	
    def accept_trace(self):
        self.data.traces.append(self.data.points)

    def update(self):
        if self.ph == None:
          return
        if self.looping != True:
          return
	self.ph.set_voltage(self.dac_voltage)
	time.sleep(0.05)
	self.adc_voltage = self.ph.get_voltage()[1]
	      # voltage and current converted into volts
	current = (self.dac_voltage - self.adc_voltage)/1000.0
        self.data.points.append( (self.adc_voltage/1000.0, current))
        if len(self.data.points) < 2:
          return
        self.plot2d.delete_lines()
        self.plot2d.line(self.data.points, self.col)
        self.dac_voltage = self.dac_voltage + self.step
        if self.dac_voltage > 5000:
          self.msgwin.msg('IV Plot Done')
          self.accept_trace()
          self.looping = False

    def intro_msg(self):
        self.clear(None)
        self.msgwin.clear()
        self.msgwin.showtext('Make the connections as shown above. The '+\
        'software changes the DAC voltage from 0 to 5V in steps and '+\
        'measure the resulting voltage across the diode. The current is '+\
        'calculated from the voltages at DAC and CH0, both are known. '+\
        'Connect a 1 uF capacitor from CH0 to ground for better results.'+\
        'You can take multiple traces. The operations are:\n')
        
        self.msgwin.showlink('Start', self.start)
        self.msgwin.showtext(' Start making the IV plot\n')
        self.msgwin.showlink('Analyze', self.analyze)
        self.msgwin.showtext(' the data using Xmgrace.\n')

        self.msgwin.showlink('Save the latest trace', self.save)
        self.msgwin.showtext(' or ')
        self.msgwin.showlink('Save all Traces', self.save_all)
        self.msgwin.showtext(' to a file named ')
        self.fntext =  Entry(None, width =20, fg = 'blue')
        self.msgwin.showwindow(self.fntext)
        self.fntext.insert(END,'iv.dat')

        self.msgwin.showlink('Display all Traces', self.show_all)
        self.msgwin.showtext(' Shows the data collected so far\n')
        self.msgwin.showlink('Clear all Traces', self.clear)
        self.msgwin.showtext(' Clears all the data ')
              
