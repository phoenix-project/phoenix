from Tkinter import *
import Image, ImageTk, time, os
from utils import Data, abs_path

photograph = 'rad.jpg'	# full path required

class rad:
    xmax  = 255
    ymax  = 100
    xlabel = 'Channel Number'
    ylabel = 'Count'
    size = [100,100]
    running = False
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
      self.ph.clear_hist()
      self.intro_msg()
      self.plot2d.setWorld(0, 0, self.xmax, self.ymax)	
      self.plot2d.mark_axes(self.xlabel,self.ylabel)
      self.plot2d.markerval = None	# Clear Markers
      self.calibrated = False
      try:
         self.plot2d.canvas.delete(self.plot2d.markertext)
      except:
         pass
      

    def exit(self):
      self.running = False
      
    def clear(self,e):
        self.plot2d.delete_lines()  
        self.data.clear()

    def set_ymax(self,w):
        d = self.scale.get()    
        self.ymax = float(d)
        self.plot2d.setWorld(0, 0, self.xmax, self.ymax)	
        self.plot2d.mark_axes(self.xlabel,self.ylabel)

    def collect_hist(self, e):
        if self.running == False:
            return
        phdata = self.ph.read_hist()
        self.plot2d.setWorld(0, 0, self.xmax, self.ymax)
        self.plot2d.mark_axes(self.xlabel, self.ylabel)
        self.data.points = []
        for k in phdata:
          energy = k[0] * self.xmax / 255.0
          self.data.points.append( (energy, k[1]) )
        self.plot2d.delete_lines()  
        self.plot2d.line(self.data.points, 'black')
#        self.data.traces.append(self.data.points)
        self.last_read_time = time.time()
        
    def update(self):
        if self.running == False:
            return
        self.collect_hist(0)

    def start(self,w):
        self.ph.start_hist()
        self.running = True
        self.msgwin.msg('Started Collecting Data')
        
    def stop(self,w):
        self.running = False
        self.ph.stop_hist()
        self.msgwin.msg('Stopped Collecting Data')
        
    def clear_hist(self,w):
        self.ph.clear_hist()
        self.plot2d.delete_lines()  
        self.msgwin.msg('Cleared Histogram Data')
        
    def save(self,e):
        fname = self.fntext.get()
        if fname == None:
          return
        self.data.save(fname)
        self.msgwin.msg('Data saved to '+ fname)

    def calibrate(self,e):
        if self.plot2d.markerval == None:
          self.msgwin.msg('Mark a Peak before calibration','red')
          return  
        try:
          chan = self.plot2d.markerval[0]
          s = self.energytext.get()
          energy = float(s)
          self.xmax = self.xmax * energy / chan
          self.xlabel = 'Energy (MeV)'
          self.plot2d.setWorld(0, 0, self.xmax, self.ymax)	
          self.plot2d.mark_axes(self.xlabel,self.ylabel)
          self.calibrated = True
          self.plot2d.canvas.delete(self.plot2d.markertext)
          self.plot2d.markerval = None
          self.msgwin.msg('Calibration done')
        except:
          self.msgwin.msg('Error occured during calibration','red')

    def autoscale(self,e):
        ymax = 10.0
        for pt in self.data.points:
          if pt[1] > ymax:
            ymax = pt[1]
        self.ymax = ymax * 1.1
        self.plot2d.setWorld(0, 0, self.xmax, self.ymax)	

    def intro_msg(self):
        self.clear(None)
        self.msgwin.clear()
        self.msgwin.showtext('Connections: (1) Blue - CH0 (2) Black - GND '+\
        '(3)Green - D3out (4) Yellow - CMP\n','red')
        self.msgwin.showtext('Connect the Radiation Detection Accessoy as '+\
        'shown in the figure. The micro controller inside Phoenix is '+\
        'interrupted every time a particle enters the detector. While '+\
        'enabled it digitizes the energy information of the particle and '+\
        'stores it in a 256 channel histogram. The following commands '+\
        'can be used to control the data acquisition process\n')
        self.msgwin.showlink('Start', self.start)
        self.msgwin.showtext(' Collecting. ')
        self.msgwin.showlink('Stop', self.stop)
        self.msgwin.showtext(' Stop Collecting. ')
        self.msgwin.showlink('Update', self.collect_hist)
        self.msgwin.showtext(' Update the Display. ')
        self.msgwin.showlink('Clear', self.clear_hist)
        self.msgwin.showtext(' Clear data and Display.\n')       
        self.msgwin.showlink('Save Histogram', self.save)
        self.msgwin.showtext(' to a text file named ') 
        self.fntext =  Entry(None, width =20, fg = 'red')
        self.msgwin.showwindow(self.fntext)
        self.fntext.insert(END,'hist.dat')
        self.msgwin.showtext('\n')
        
        self.scale =  Scale(None, command = self.set_ymax, resolution = 100,\
          from_ = 100, to=10000, orient=HORIZONTAL, length=100, showvalue=0)
        self.scale.set(self.ymax)
        self.msgwin.showwindow(self.scale)
        self.msgwin.showtext(' Change the Vertical Axis. For auto scaling ')
        self.msgwin.showlink('Click Here\n', self.autoscale)

        self.msgwin.showtext(' To calibrate, click on a known peak, enter '+\
        ' the corresponding energy ')       
        self.energytext =  Entry(None, width =10, fg = 'red')
        self.msgwin.showwindow(self.energytext)
        self.energytext.insert(END,'5.485')
        self.msgwin.showtext(' MeV and ')
        self.msgwin.showlink('Click Here\n', self.calibrate)
       
