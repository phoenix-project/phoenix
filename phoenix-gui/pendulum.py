from Tkinter import *
import Image, ImageTk, os, time
from utils import Data, abs_path

photograph = 'pend_dig.jpg'	# full path required 

class pend:
    NP = 400
    tmax = 5.0		# We digitize oscillations for 10 seconds
    looping = False
    xlabel = 'Seconds'
    ylabel = 'Volts'
    size = [100,100]
    scale = None    
    delay = 0.0
    
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
      
    def set_tmax(self,w):
        d = self.scale.get()    
        self.tmax = float(d)
        self.plot2d.setWorld(0, -5, self.tmax, 5)	
        self.plot2d.mark_axes(self.xlabel,self.ylabel)
        
    def clear(self,e):
        if self.looping == True:
            return
        self.plot2d.delete_lines()  
        self.data.clear()

    def save(self,e):
        fname = self.fntext.get()
        if fname == None:
          return
        self.data.save(fname)
        self.msgwin.msg('Data saved to '+ fname)

    def calc_g(self,e):
        if self.data.points == []:
            return
        x = self.lentext.get()
        try:
            L = float(x)
        except:
            self.msgwin.msg('Set the length of the rod', 'red')
            return

        import phmath, math
        dat = []
        for k in self.data.points:
           dat.append([k[0], k[1]])
        res = phmath.fit_dsine(dat)
        fit = []
        exp = []
        for k in res[0]: 
            fit.append([k[0],k[2]])
            exp.append([k[0],k[3]])
        self.data.traces.append(fit)
       	self.col = self.data.get_col()
        self.plot2d.line(fit, self.col)
       	self.col = self.data.get_col()
        self.plot2d.line(exp, self.col)

        D = res[1][4]
        T = 1.0 / res[1][1]
        r = 0.14		# radius of the rod
        R = 1.27		# radius of the ball
        density = 7.8		# density of iron
        m_rod = math.pi * r**2 * L * density
        m_ball = math.pi * 4 / 3 * R**3 * density
#        print m_rod,'',m_ball
        Lprime = ( (m_rod * L**2)/3 + (m_ball * 2/5 * R**2) + m_ball * \
          (L+R)**2 ) / ( (m_rod * L)/2 + m_ball*(L+R) )

        g = 4.0 * math.pi**2 * Lprime / (T * T)
#        print T, Lprime, g, D 
        ss = 'T = %4.3f seconds. Length = %4.2f | g = %4.0f \
cm/sec2 | Damping factor = %4.3f\n'%(T,L,g,D)
        self.msgwin.showtext(ss)
#        g2 = 4.0 * math.pi**2 * L / (T * T)
        
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
        self.msgwin.msg('Starting Pendulum Waveform digitization')
	self.looping = True

	v = self.ph.get_voltage_bip()		# First reading is taken
	self.start_time = v[0]			# Remember starting time
        self.data.points = [(0.0, v[1]/1000.0)]	# initialize the list
        
    def accept_trace(self):
        self.data.traces.append(self.data.points)

    def update(self):
        if self.looping == False:
            return
        val = self.ph.get_voltage_bip()
        elapsed = val[0] - self.start_time
        self.data.points.append( (elapsed, val[1]/1000.0) )
        self.plot2d.delete_lines()
        self.plot2d.line(self.data.points, self.col)
        if elapsed >= self.tmax:
          self.msgwin.msg('Digitization done for %2.1f seconds'%elapsed)
          self.accept_trace()
          self.looping = False

    def refresh(self,e):
        if self.looping == True:
            return
        self.intro_msg()

    def intro_msg(self):
        self.clear(None)
        self.msgwin.clear()
        self.msgwin.showtext('Connect one lead from the motor to GND. '+\
        'Other lead to CH0 through the non-inverting amplifier (Rg=100) '+\
        'and level shifter. Oscillate it and :'+\
        '\nClick ')
        self.msgwin.showlink('Start', self.start)
        self.msgwin.showtext('  to Digitize for ')
        if self.scale != None: self.scale.destroy()
        self.scale =  Scale(None, command = self.set_tmax, \
          from_ = 1, to=20, orient=HORIZONTAL, length=100, showvalue=1)
        self.scale.set(int(self.tmax))
        self.msgwin.showwindow(self.scale)
        self.msgwin.showtext(' Seconds. After capturing a waveform\n')
        self.msgwin.showlink('Click Here', self.calc_g)
        
        self.msgwin.showtext(' to calculate the value of "g" by extracting '+\
        '"T" from it and assuming Length of the rod =')
        self.lentext =  Entry(None, width = 4, fg = 'red')
        self.msgwin.showwindow(self.lentext)
        self.lentext.insert(END,'11.0')
        self.msgwin.showtext(' cm. and Bob diameter = 2.54 cm')
        
        
        self.msgwin.showtext('\nClicking Start in between will restart '+\
        'digitization process. After one '+\
        'digitization is over, repeating the process will collect '+\
        'another set of data.')

        self.msgwin.showlink('\nSave the latest trace', self.save)
        self.msgwin.showtext(' or ')
        self.msgwin.showlink('Save all Traces', self.save_all)
        self.msgwin.showtext(' to the text file')
        self.fntext =  Entry(None, width =15, fg = 'red')
        self.msgwin.showwindow(self.fntext)
        self.fntext.insert(END,'pend.dat')
        self.msgwin.showtext('  ')
        self.msgwin.showlink('Display all Traces', self.show_all)
        self.msgwin.showtext('   ')
        self.msgwin.showlink('Clear all Traces', self.clear)
        self.msgwin.showtext('   ')
        self.msgwin.showlink('Xmgrace', self.analyze)
        self.msgwin.showtext('   ')
        self.msgwin.showlink('Refresh', self.refresh)
        self.msgwin.showtext('\n')
 
              
