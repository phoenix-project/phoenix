from Tkinter import *
import Image, ImageTk, time

from utils import Data, abs_path

photograph = 'cap.jpg'	# source file and 'pics' must be at same place

class cap:
    NP = 200
    adc_delay = 20
    delay_vals = [10,20,50,100,200,500,1000]
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
      
    def enter(self, fd):	#Phoenix handler 'ph' is set by the caller
        self.intro_msg()
        self.ph = fd
        try:
            self.ph.select_adc(0)
            self.ph.set_adc_size(2)
        except:
            self.msgwin.msg('Connection NOT Established','red')
                
    def exit(self):		# Do cleanup here
        try:
            self.ph.disable_set()
        except:
            pass
            
    def update(self):
        pass
      
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
        
    def capture_trace(self): # Collect data and store in object 'data'
        # All conversion to be done here. setWorld according to 'trace'
        # xscale and yscale are specified
        # if axes are shown in different units    
        phdata = self.ph.read_block(self.NP, self.adc_delay, 0)
        self.data.points = []
        for k in phdata:
          self.data.points.append( (k[0]/1000.0, k[1]/1000.0) )
            #microsec -> millisec ; millivolts -> volts
        self.data.traces.append(self.data.points)
        last = self.data.points[-1][0]
        second = self.data.points[-2][0]
        xmax = last + (last-second)

        self.plot2d.setWorld(0, 0, xmax, 5)	# Set scale factors
        self.plot2d.mark_axes(self.xlabel, self.ylabel)	 # axes & labels
        self.plot2d.line(self.data.points, self.data.get_col())
        
    def discharge(self,w):
        self.ph.write_outputs(8)
        time.sleep(1)
        self.ph.enable_set_low(3)
        self.capture_trace()

    def charge(self,w):
        self.ph.write_outputs(0)
        time.sleep(1)
        self.ph.enable_set_high(3)
        self.capture_trace()
        
    def set_adc_delay(self,w):
        d = self.adc_scale.get()    
        self.adc_delay = self.delay_vals[d]
        if self.ph == None:
            return
        self.ph.set_adc_delay(self.adc_delay)
        self.plot2d.setWorld(0, 0, self.NP * self.adc_delay/1000.0, 5)
        self.plot2d.mark_axes(self.xlabel, self.ylabel)

    def calc_cap(self,e):
        if self.data.points == []:
            return
        x = self.restext.get()
        try:
            R = float(x)
        except:
            self.msgwin.msg('Set the Resistance value', 'red')
            return

        import phmath, math
        dat = []
        for k in self.data.points:
           dat.append([k[0], k[1]])
        res = phmath.fit_exp(dat)
        fit = []
        for k in res[0]: 
            fit.append([k[0],k[2]])
        self.data.traces.append(fit)
       	self.col = self.data.get_col()
        self.plot2d.line(fit, self.col)

        RC = -1.0/res[1][1]
        C = RC/R
#        print res[1][1], RC, R, C
        ss = 'RC = %4.3f . C = %4.3f\n'%(RC,C)
        self.msgwin.showtext(ss)

    def refresh(self,e):
        self.intro_msg()

    def intro_msg(self):
        self.clear(None)
        self.msgwin.clear()
        self.msgwin.showtext('Connect the Capacitor from CH0 to GND and '+\
        'Resistor from D3out to CH0. The Blue Texts are the Commands.\n')
        self.msgwin.showlink('Charge', self.charge)
        self.msgwin.showtext('  or   ')
        self.msgwin.showlink('Discharge.', self.discharge)
        self.msgwin.showtext('       ')
        self.msgwin.showlink('Fit the Discharge Curve', self.calc_cap)
        self.msgwin.showtext(' and calculate the value of capacitance for R = ')
        self.restext =  Entry(None, width = 4, fg = 'red')
        self.msgwin.showwindow(self.restext)
        self.restext.insert(END,'1.0')
        self.msgwin.showtext(' KOhm.\n')
        
        self.msgwin.showlink('Save Last Trace', self.save)
        self.msgwin.showtext(' or ')
        self.msgwin.showlink('Save all Traces', self.save_all)
        self.msgwin.showtext(' to a text file named ') 
        self.fntext =  Entry(None, width =20, fg = 'red')
        self.msgwin.showwindow(self.fntext)
        self.fntext.insert(END,'cap.dat')
        self.msgwin.showtext(' ')
        self.msgwin.showlink('Clear Traces', self.clear)
        self.msgwin.showtext('   ')
        self.msgwin.showlink('Xmgrace', self.analyze)
        self.msgwin.showtext('    ')
        self.msgwin.showlink('Refresh', self.refresh)
        self.msgwin.showtext('\n')

        self.adc_scale =  Scale(None, command = self.set_adc_delay, \
          from_ = 0, to=6, orient=HORIZONTAL, length=100, showvalue=0)
        self.adc_scale.set(1)
        self.msgwin.showwindow(self.adc_scale)
        self.msgwin.showtext(' Change time scale according to RC time constant.\n')
       
