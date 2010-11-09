from Tkinter import *
import Image, ImageTk, os, time, math
from utils import Data, abs_path

photograph = 'gravity.jpg'	# full path required 

class gravity:
    NP = 400
    tmax = 10.0		# We digitize oscillations for 10 seconds
    maxcount = 10
    looping = False
    xlabel = 'Number'
    ylabel = 'g'
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
      self.intro_msg()
      self.plot2d.setWorld(0, -5, self.tmax, 5)	
      self.plot2d.mark_axes(self.xlabel,self.ylabel)

    def exit(self):
      self.looping = False
      
    def update(self):
        pass

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
        
    def attach(self,e):
        x = self.lentext.get()
        try:
            self.length = float(x)
        except:
            self.msgwin.msg('Set the Height', 'red')
            return

        if self.ph == None:
            self.msgwin.msg('Connection not made yet', 'red')
            return
        self.ph.write_outputs(1)
        self.msgwin.msg('Powered the Electromagnet')
        
    def measure(self,e):
        t = self.ph.clr2rtime(0,0)
        if t < 0:
             self.msgwin.msg('Timeout Error', 'red')
             return
        elif t < 20:
             self.msgwin.msg('Connection Error', 'red')
             return
        t = t + 4000.0   # 4 ms correction for magnetic retention
        t = t * 1.0e-6   # usec to sec
        print t, self.length
        g = 2.0 * self.length / t ** 2
        self.msgwin.showtext('\n%7.6f\t%4.1f'%(t,g))
        self.msgwin.msg('Done')

    def refresh(self,e):
        self.intro_msg()

    def intro_msg(self):
        self.msgwin.clear()
        self.msgwin.showtext('Connect the Electromagnet between Digital '+\
        'Output D0 and GND. '+\
        'Connect the loudspeaker between GND and the input of the inverting '+\
        'amplifier and set the gain resistor to 100 Ohms. '+\
        ' Amplifier output goes to Digital Input D0 through a 1K resistor.\n')

        self.msgwin.showlink('Click Here', self.attach)
        self.msgwin.showtext(' to power the Electromagnet.')
        
        self.msgwin.showtext(' Height = ')
        self.lentext =  Entry(None, width = 5, fg = 'red')
        self.msgwin.showwindow(self.lentext)
        self.lentext.insert(END,'30.0')
        self.msgwin.showtext(' cm.')

        self.msgwin.showlink('Click Here', self.measure)
        self.msgwin.showtext(' to Release the Ball from the magnet.')
