from Tkinter import *
import Image, ImageTk, os
from utils import Data, abs_path

photograph = 'induction.jpg'	# full path required 

class induction:
    NP = 200
    adc_delay = 500
    delay_vals = [200,500,1000]
    looping = False
    xlabel = 'milli seconds'
    ylabel = 'Volts'
    size = [100,100]
    
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

    def enter(self,fd):
        self.plot2d.setWorld(0, -5, self.NP * self.adc_delay/1000.0, 5)
        self.plot2d.mark_axes(self.xlabel, self.ylabel)
        self.intro_msg()
        self.ph = fd
        try:
            self.ph.select_adc(0)
            self.ph.set_adc_size(2)
        except:
            self.msgwin.msg('Connection NOT Established','red')
        
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

    def set_adc_delay(self,w):
        d = self.adc_scale.get()    
        self.adc_delay = self.delay_vals[d]
        if self.ph == None:
            return
        self.ph.set_adc_delay(self.adc_delay)
        self.plot2d.setWorld(0, -5, self.NP * self.adc_delay/1000, 5)
        self.plot2d.mark_axes(self.xlabel, self.ylabel)
#------------------------------------------------------------------        
        
    def start(self,e):
        if self.ph == None:
          self.msgwin.msg('Connection not made yet', 'red')
          return
        phdata = self.ph.read_block(self.NP, self.adc_delay, 1)
        if phdata == None: 
            return

        self.data.points = []
        for k in phdata:
          self.data.points.append( (k[0]/1000.0, k[1]/1000.0) ) # scale & copy
        
	self.limit = 0.0		# Find the present signal level
	for p in self.data.points:
          if abs(p[1]) > self.limit:
	    self.limit = abs(p[1]) + 0.1
	self.looping = True
        self.msgwin.msg('Scanning for Waveform (amplitude > %4.3f V)'%self.limit)
#	print self.limit
	
    def get_peaks(self):
        vmin = 5.0
        vmax = -5.0
        t1 = t2 = 0
        for p in self.data.points:
          if p[1] < vmin:
            vmin = p[1]
            t1 = p[0]
	  if p[1] > vmax:
	    vmax = p[1]
	    t2 = p[0]
#        print vmin, vmax
        if t1 < t2:			# First peak is first
            return (t1,vmin), (t2,vmax)
        else:
            return (t2,vmax),(t1,vmin)

    def accept_trace(self):
#        print self.data.points
        self.data.traces.append(self.data.points)
        self.msgwin.msg('Waveform Captured. Click on Scan CH0 to repeat')
        
    def update(self):
        if self.ph == None:
          return
        if self.looping != True:
          return
        try:
          data = self.ph.read_block(self.NP, self.adc_delay, 1)
          if data == None: return
        except: 
          return
        self.data.points = []
        for k in data:
          self.data.points.append( (k[0]/1000.0, k[1]/1000.0) )
        self.plot2d.delete_lines()
        self.plot2d.line(self.data.points,'black')
	for p in self.data.points:
	  if abs(p[1]) > self.limit:
	    self.peaks = self.get_peaks()
	    tmax = self.NP * self.adc_delay / 1000.0 # micro to milli secs
            if self.peaks[0][0] > 0.2*tmax and self.peaks[1][0] < 0.8*tmax:
  	      self.looping = False
              self.accept_trace()
              break
 
    def intro_msg(self):
        self.clear(None)
        self.msgwin.clear()
        self.msgwin.showtext('Connect the coil between Ground and the input '+\
        'of the Level Shifting Amplifier and the output of the Amplifier '+\
        'to ADC input CH0.\nNow Click ')
        self.msgwin.showlink('HERE', self.start)
        self.msgwin.showtext(' to start scanning the CH0 input at regular '+\
        'intervals. A horizontal trace now apprears on the screen.\n'+\
        'Drop the magnet into the coil from some height. If the timing '+\
        'coinsides with the scanning, the induced voltage will be captured. '+\
        'Keep dropping the magnet till this happens. You can repeat the '+\
        'whole process to acquire several waveforms by changing the speed '+\
        'of the magnet, orientation etc.\n')
        self.msgwin.showlink('View All', self.show_all)
        self.msgwin.showtext(' Display all the waveforms captured so far.\n')

        self.msgwin.showlink('Save', self.save)
        self.msgwin.showtext(' the latest trace or ')
       
        self.msgwin.showlink('Save all Traces', self.save_all)
        self.msgwin.showtext(' to a file named ')
        self.fntext =  Entry(None, width =20, fg = 'red')
        self.msgwin.showwindow(self.fntext)
        self.fntext.insert(END,'ind.dat')
        self.msgwin.showtext('\n')
        self.msgwin.showlink('Analyze', self.analyze)
        self.msgwin.showtext(' Analysis of data using Xmgrace program.\n')
        self.msgwin.showlink('Clear all Traces', self.clear)
        self.msgwin.showtext(' Clear all the data collected.')
 

              
