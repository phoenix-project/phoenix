from Tkinter import *
import Image, ImageTk, time, os
from utils import Data, abs_path

photograph = 'usound.jpg'	# full path required

class sound:
    NP = 200
    adc_delay = 10
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
        self.ph.write_outputs(0)
        self.ph.set_pulse_width(13)
        self.plot2d.setWorld(0, -5, self.NP * self.adc_delay/1000.0, 5)
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
        self.ph.enable_pulse_high(3)
        data = self.ph.read_block(self.NP, self.adc_delay, 1)
        self.data.points = []
        for k in data:
          self.data.points.append( (k[0]/1000.0, k[1]/1000.0) )
        self.plot2d.line(self.data.points, self.data.get_col())
        self.data.traces.append(self.data.points)
        self.ph.write_outputs(0);
        
    def set_adc_delay(self,w):
        d = self.adc_scale.get()    
        self.adc_delay = self.delay_vals[d]
        if self.ph == None:
            return
        self.ph.set_adc_delay(self.adc_delay)
        self.plot2d.setWorld(0, -5, self.NP * self.adc_delay/1000.0, 5)
        self.plot2d.mark_axes(self.xlabel, self.ylabel)

    def ms_delay(self,e):
        self.ph.write_outputs(0)
        self.ph.set_pulse_width(13)
        self.ph.set_pulse_polarity(0)
        t = self.ph.pulse2rtime(3,3)
        if t < 0:
            self.msgwin.showtext('\nTime out on Input D3','red')
            return
        self.msgwin.showtext('%4.0f'%t)
    
    def refresh(self,e):
        self.msg_intro()

    def msg_intro(self):
        self.clear(None)
        self.msgwin.clear()
        self.msgwin.showtext('Connect the Transmitter Piezo between Digital '+\
        'output D3 and Ground. Connect the Receiver Piezo between Ground '+\
        'and the Inverting Amplifier Input. Set a gain resistor of 100. '+\
        'Connect the Output of the amplifier to the level shifter and '+\
        'level shifter output to Ch0. If the Amplitude is less, use one '+\
        'more Inverting amplifier in series.')

        self.msgwin.showlink('View Waveform', self.show_waveform)
        self.msgwin.showtext(' View the output of the receiver piezo.\n')
        
        self.msgwin.showlink('Save Last Trace', self.save)
        self.msgwin.showtext(' or ')
        self.msgwin.showlink('Save all Traces', self.save_all)
        self.msgwin.showtext(' to a text file named ') 
        self.fntext =  Entry(None, width =20, fg = 'red')
        self.msgwin.showwindow(self.fntext)
        self.fntext.insert(END,'sound.dat')
        self.msgwin.showtext(' ')
        self.msgwin.showlink('Clear all Traces', self.clear)
        self.msgwin.showtext(' to remove all the plots.\n')
        self.msgwin.showtext('\nConnect the Inverting Amplifier Output '+\
        'to Digital Input D3 through a 1K Series resistance to.')
        self.msgwin.showlink('Measure Time Delay', self.ms_delay)

        self.msgwin.showtext(' or ')
        self.msgwin.showlink('Refresh', self.refresh)
        self.msgwin.showtext('\n')
       
