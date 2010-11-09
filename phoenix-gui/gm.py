from Tkinter import *
import Image, ImageTk, os, time, math
from utils import Data, abs_path

photograph = 'gmcounter.jpg'	# full path required 

class gm:
    NP = 400
    countrate = 100.0		# Assume a 100 Hz count rate
    numtrials = 5		# 5 trials default
    duration = 1		# count for one second
    tube_voltage = 0.0
    VMIN = 300.0
    VOPT = 500.0
    VMAX = 902.0
    looping = False
    xlabel = 'Trial'
    ylabel = 'Count'
    size = [100,100]
    scale = None    
    
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
      self.plot2d.setWorld(0, 0, self.countrate, self.numtrials)	
      self.plot2d.mark_axes(self.xlabel,self.ylabel)
      self.tube_voltage = self.ph.gm_set_voltage(self.VOPT)
      self.intro_msg()
      
    def exit(self):
      self.looping = False
      
    def clear(self,e):
        if self.looping == True: return
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
        x = self.durationtext.get()
        try:
            self.duration = int(x)
        except:
            self.msgwin.msg('Set the Duration of Counting', 'red')
            return

        x = self.trialstext.get()
        try:
            self.numtrials = int(x)
        except:
            self.numtrials = 5

        if self.ph == None:
            self.msgwin.msg('Connection not made yet', 'red')
            return
        if self.looping == False:    		# Same color if restarted
        	self.col = self.data.get_col()
        
        self.tube_voltage = self.ph.gm_set_voltage(self.tube_voltage)
        self.msgwin.msg('GM tube Counting Radiation.')
        self.msgwin.label.update()
	self.count = 0
        gmc = self.ph.gm_get_count(self.duration)
        self.msgwin.showtext('\nCounts : %d '%(gmc))
        self.data.points = [(self.count, gmc)]
        self.plot2d.setWorld(0, 0, self.numtrials, gmc * 1.5 + 5)
        self.xlabel = 'Trial'
        self.plot2d.mark_axes(self.xlabel,self.ylabel)
        self.count = self.count + 1
	self.looping = True
        self.doing_gmchar = False

    def start_gmgraph(self,e):
        x = self.durationtext.get()
        try:
            self.duration = int(x)
        except:
            self.msgwin.msg('Set the Duration of Counting', 'red')
            return
        if self.looping == False:    		# Same color if restarted
        	self.col = self.data.get_col()
        self.msgwin.msg('Drawing GM tube Characteristic (will take time)')
        self.msgwin.label.update()
        self.count = 0
        self.tube_voltage = self.ph.gm_set_voltage(self.VOPT)
        gmc_max = self.ph.gm_get_count(self.duration)
        self.plot2d.setWorld(self.VMIN, 0, self.VMAX*1.1, gmc_max * 2 + 5)	
        self.xlabel = 'Voltage'
        self.plot2d.mark_axes(self.xlabel,self.ylabel)
	self.tube_voltage = self.ph.gm_set_voltage(self.VMIN)
        gmc = self.ph.gm_get_count(self.duration)
        self.msgwin.showtext('\n(%4.0f,%d) '%(self.tube_voltage,gmc))
        self.data.points = [(self.tube_voltage, gmc)]
        self.count = self.count + 1
	self.looping = True
        self.doing_gmchar = True

    def accept_trace(self):
        self.data.traces.append(self.data.points)

    def update(self):
        if self.looping == False:
            return
        if self.doing_gmchar == True:
            if self.tube_voltage < 400:
                self.tube_voltage = self.ph.gm_set_voltage(self.tube_voltage + 20)
            else:
                self.tube_voltage = self.ph.gm_set_voltage(self.tube_voltage + 50)
            gmc = self.ph.gm_get_count(self.duration)
            self.data.points.append((self.tube_voltage, gmc))
            self.plot2d.delete_lines()
            self.plot2d.line(self.data.points, self.col, smooth=False)
            self.msgwin.showtext('(%4.0f,%d) '%(self.tube_voltage,gmc))
            self.count = self.count + 1
            if self.tube_voltage > self.VMAX:
                self.looping = False
                self.msgwin.msg('GM Tube Characteristic Done.')
#                self.ph.gm_set_voltage(self.VOPT)
                self.set_tv(None)
                self.accept_trace()
        else:
            gmc = self.ph.gm_get_count(self.duration)
            self.data.points.append((self.count, gmc))
            self.plot2d.delete_lines()
            self.plot2d.line(self.data.points, self.col, smooth=False)
            self.msgwin.showtext('%d '%(gmc))
            self.count = self.count + 1
            if self.count >= self.numtrials:
                self.looping = False
                self.msgwin.msg('Counting Over after %d trials'%self.numtrials)
                self.accept_trace()

    def set_tv(self, e):
        ss =  self.tv_text.get()
        try:
           vset = float(ss)
        except:
           vset = 0
        self.tube_voltage = self.ph.gm_set_voltage(vset)
        ss = '%5.0f'%self.tube_voltage
        self.gmtv_value.set(ss)
        
    def refresh(self,e):
        self.intro_msg()

    def intro_msg(self):
        self.msgwin.clear()
        self.msgwin.showtext('Connections: (1)Yellow - CNTR (2) Green - CH0 '+\
        '(3) Blue - PWG (4) Black - GND (5) Red - 5V.\n','red')
        self.msgwin.showtext('Enter the Tube voltage ')
        self.tv_text =  Entry(None, width = 5, fg = 'red')
        self.msgwin.showwindow(self.tv_text)
        self.tv_text.insert(END, '500')
        self.msgwin.showtext('Volts and ')
        self.msgwin.showlink('Click Here ', self.set_tv)
        self.msgwin.showtext(' to set it. Current Tube Voltage is ')
        self.gmtv_value = StringVar()
        self.gmtv_label =  Label(None, width=5, textvariable = self.gmtv_value)
        self.msgwin.showwindow(self.gmtv_label)
        ss = '%5.0f'%self.tube_voltage
        self.gmtv_value.set(ss)
        self.msgwin.showtext('Volts\n')
        
        self.msgwin.showtext('Set the duration of Counting to')
        self.durationtext =  Entry(None, width = 5, fg = 'red')
        self.msgwin.showwindow(self.durationtext)
        self.durationtext.insert(END,'1')
        self.msgwin.showtext('seconds and number of trials to')
        self.trialstext =  Entry(None, width = 5, fg = 'red')
        self.msgwin.showwindow(self.trialstext)
        self.trialstext.insert(END,str(self.numtrials))

        self.msgwin.showtext('.')
        self.msgwin.showlink('Click Here', self.start)

        self.msgwin.showtext(' to start counting. ')
        self.msgwin.showtext('For tube Characteristic ')
        self.msgwin.showlink('Click Here', self.start_gmgraph)
        self.msgwin.showtext('\n');

        self.msgwin.showlink('Save the latest trace', self.save)
        self.msgwin.showtext(' or ')
        self.msgwin.showlink('Save all Traces', self.save_all)
        self.msgwin.showtext(' to a text file named ')
        self.fntext =  Entry(None, width =15, fg = 'red')
        self.msgwin.showwindow(self.fntext)
        self.fntext.insert(END,'gmcount.dat')
        self.msgwin.showtext(' or ')
        self.msgwin.showlink('Analyze', self.analyze)
        self.msgwin.showtext(' data online using Xmgrace.\n')
        self.msgwin.showtext('You can also do ')
        self.msgwin.showlink('Display all Traces', self.show_all)
        self.msgwin.showtext(' , ')
        self.msgwin.showlink('Clear all Traces', self.clear)
        self.msgwin.showtext(' or ')
        self.msgwin.showlink('Refresh This Window', self.refresh)
        self.msgwin.showtext('\n')
