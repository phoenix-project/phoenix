from Tkinter import *
import Image, ImageTk, time, os
from utils import Data, abs_path

photograph = 'mono.jpg'	# full path required

class mono:
    NP = 200
    adc_delay = 20
    delay_vals = [10,20,50,100,200,500,1000]
    looping = False
    xlabel = 'milli seconds'
    ylabel = 'Volts'
    adc_scale = None
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
      
    def enter(self, fd):	#Phoenix handler set by the caller
        self.ph = fd
        self.ph.select_adc(0)
        self.ph.set_adc_size(1)
        self.ph.set_pulse_width(1)
        self.plot2d.setWorld(0, 0, self.NP * self.adc_delay/1000.0, 5)
        self.plot2d.mark_axes(self.xlabel, self.ylabel)
        self.msg_intro()
      
    def exit(self):		# Do cleanup here
        self.ph.disable_set()

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

    def save_all(self,e):
        fname = self.fntext.get()
        if fname == None:
          return
        self.data.save_all(fname)
        self.msgwin.msg('Data saved to '+ fname)
        
    def show_waveform(self,w):
        self.ph.enable_pulse_low(3)
        data = self.ph.read_block(self.NP, self.adc_delay, 0)
        self.data.points = []
        for k in data:
          self.data.points.append( (k[0]/1000.0, k[1]/1000.0) )
        self.plot2d.line(self.data.points, self.data.get_col())
        self.data.traces.append(self.data.points)
        self.ph.write_outputs(8);
        
    def set_adc_delay(self,w):
        d = self.adc_scale.get()    
        self.adc_delay = self.delay_vals[d]
        if self.ph == None:
            return
        self.ph.set_adc_delay(self.adc_delay)
        self.plot2d.setWorld(0, -5, self.NP * self.adc_delay/1000.0, 5)
        self.plot2d.mark_axes(self.xlabel, self.ylabel)

    def ms_delay(self,e):
        self.ph.write_outputs(8)
        self.ph.set_pulse_width(1)
        self.ph.set_pulse_polarity(1)
        t = self.ph.pulse2ftime(3,3)
        if t < 0:
            self.msgwin.showtext('\nTime out on Input D3','red')
            return
        self.msgwin.showtext('\nMonoshot Delay = ' + '%4.0f'%(t) + ' usec.')
    
    def refresh(self,e):
        self.msg_intro()

    def msg_intro(self):
        self.clear(None)
        self.msgwin.clear()
        self.msgwin.showtext('Power the Monostable Multivibrator circuit '+\
        'made using IC555 from the 5V Output socket. Connect the Trigger '+\
        'Input of 555 (pin number 2) to Digital Output D3.\n')

        self.msgwin.showlink('View Waveform', self.show_waveform)
        self.msgwin.showtext(' View the output of the circuit.\n')
        self.adc_scale =  Scale(None, command = self.set_adc_delay, \
          from_ = 0, to=6, orient=HORIZONTAL, length=100, showvalue=0)
        self.adc_scale.set(1)
        self.msgwin.showwindow(self.adc_scale)
        self.msgwin.showtext(' Change time scale if required.\n')
        
        self.msgwin.showlink('Save Last Trace', self.save)
        self.msgwin.showtext(' or ')
        self.msgwin.showlink('Save all Traces', self.save_all)
        self.msgwin.showtext(' to a text file named ') 
        self.fntext =  Entry(None, width =20, fg = 'red')
        self.msgwin.showwindow(self.fntext)
        self.fntext.insert(END,'mono555.dat')
        self.msgwin.showtext(' ')
        self.msgwin.showlink('Clear all Traces', self.clear)
        self.msgwin.showtext(' to remove all the plots.\n')
        self.msgwin.showtext('\nConnect 555 output to Digital input D3. ')
        self.msgwin.showlink('Measure Time Delay', self.ms_delay)

        self.msgwin.showtext('  .To Refresh Text Window ')
        self.msgwin.showlink('Click Here', self.refresh)
       
