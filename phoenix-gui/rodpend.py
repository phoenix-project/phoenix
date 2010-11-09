from Tkinter import *
import Image, ImageTk, os, time, math
from utils import Data, abs_path

photograph = 'lb_rod.jpg'	# full path required 

class rodpend:
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
      self.ph.select_adc(0)
      self.ph.set_adc_size(2)
      self.intro_msg()
      self.plot2d.setWorld(0, -5, self.tmax, 5)	
      self.plot2d.mark_axes(self.xlabel,self.ylabel)

    def exit(self):
      self.looping = False
      
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
        x = self.lentext.get()
        try:
            self.length = float(x)
        except:
            self.msgwin.msg('Set the length of the Pendulum', 'red')
            return

        x = self.numtext.get()
        try:
            self.maxcount = int(x)
        except:
            self.maxcount = 10
        self.tmax = self.maxcount

        if self.ph == None:
            self.msgwin.msg('Connection not made yet', 'red')
            return
        if self.looping == False:    		# Same color if restarted
        	self.col = self.data.get_col()
        self.msgwin.msg('Starting Measurement of gravity using Rod Pendulum')
	self.count = 0
        t = self.ph.pendulum_period(3)	# Every alternate rising edge
#	t = self.ph.multi_r2rtime(3,1)
	if t < 0:
          self.msgwin.msg('Pendulum Period Timeout Error', 'red')
          return
        t = t/1000000.0
        self.pisqr = math.pi ** 2
        g = 4.0 * self.pisqr * 2.0 * self.length / (3.0 *  t * t)
        self.msgwin.showtext('\nPeriod    Gravity')
        self.msgwin.showtext('\n%6.5f\t%4.1f'%(t,g))
#        print self.pisqr, self.length, t, g
        self.data.points = [(self.count, g)]
        self.plot2d.setWorld(0, 0, self.tmax, g*1.2)	
        self.plot2d.mark_axes(self.xlabel,self.ylabel)
	self.looping = True

    def accept_trace(self):
        self.data.traces.append(self.data.points)

    def update(self):
        if self.looping == False:
            return
        t = self.ph.pendulum_period(3)	# Every alternate rising edge
        if t < 0:
          self.msgwin.msg('Pendulum Period Timeout Error', 'red')
          self.looping = False
          return
        print t
        t = t/1000000.0
        self.pisqr = math.pi ** 2
        g = 4.0 * self.pisqr * 2.0 * self.length / (3.0 *  t * t)
        self.data.points.append( (self.count, g) )
        self.plot2d.delete_lines()
        self.plot2d.line(self.data.points, self.col)
        self.msgwin.showtext('\n%6.5f\t%4.1f'%(t,g))
        self.count = self.count + 1
        if self.count >= self.maxcount:
          self.looping = False
          self.msgwin.msg('Measured gravity %d times'%self.count)
          self.accept_trace()
        time.sleep(t/2)		# Always measure in the same direction

    def refresh(self,e):
        self.intro_msg()

    def intro_msg(self):
#        self.clear(None)
        self.msgwin.clear()
        self.msgwin.showtext('Connect the Light Barrier as shown in the '+\
        'photograph and set the pendulum oscillating. Phoenix will measure '+\
        'the Period of the pendulum and calculate the value of acceleration '+\
        'due to gravity. Measure the length of the pendulum and enter it '+\
        'The pendulum must be vertical in its resting position.\n')

        self.msgwin.showtext('Oscillate the Pendulum and ')
        self.msgwin.showlink('Click Here', self.start)
        self.msgwin.showtext(' to start the measurements.')
        
        self.msgwin.showtext(' Length = ')
        self.lentext =  Entry(None, width = 5, fg = 'red')
        self.msgwin.showwindow(self.lentext)
        self.lentext.insert(END,'7.0')
        self.msgwin.showtext(' cm. Number of measurements = ')
        self.numtext =  Entry(None, width = 5, fg = 'red')
        self.msgwin.showwindow(self.numtext)
        self.numtext.insert(END,str(self.maxcount))

        self.msgwin.showlink('\nSave the latest trace', self.save)
        self.msgwin.showtext(' or ')
        self.msgwin.showlink('Save all Traces', self.save_all)
        self.msgwin.showtext(' to a text file named ')
        self.fntext =  Entry(None, width =15, fg = 'red')
        self.msgwin.showwindow(self.fntext)
        self.fntext.insert(END,'rodpend.dat')
        self.msgwin.showtext(' or ')
        self.msgwin.showlink('Analyze', self.analyze)
        self.msgwin.showtext(' data online using Xmgrace.\n')
        self.msgwin.showlink('Display all Traces', self.show_all)
        self.msgwin.showtext(' , ')
        self.msgwin.showlink('Clear all Traces', self.clear)
        self.msgwin.showtext(' or ')
        self.msgwin.showlink('Refresh This Window', self.refresh)
        self.msgwin.showtext('\nCalculated g will be plotted.')
