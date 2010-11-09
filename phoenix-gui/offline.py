import array, time, sys, os, struct
from math import *

"""
Dummy for phm.py
Just enable to browse the menus of guideme.py
"""

WIDTH =     300.0    # used by plot()
HALF_HEIGHT=100.0
YMAX     = 5000.0    #5000 mV


def phm(dev = None):
    object = Phm()
    return object


BUFSIZE      = 1802            # status + adcinfo + 800 data

class Phm:
    buf = array.array('B',BUFSIZE * [0])    # unsigned character array, Global
    seeprom_active = 0    
    num_samples = 100        # 1 to 800
    num_chans = 1            # 1 to 4
    current_chan = 1        # 0 to 3
    adc_size = 1            # 1 or 2 bytes
    adc_delay = 10            # 10 to 1000 usecs, Atmega16 
    adc_format_bip = 0;        # 1 if through level shifter amplifier
    maxwaitds = 40            # timeout = 40 * 50 msec
    pulse_width = 13        # 1 to 1000 usecs
    pulse_pol = 0            # HIGH TRUE (0) or  LOW TRUE (1)
    handle = None
    usb_dev = False
    last_message = ''
    
    colors = ['black', 'red', 'green', 'blue']
    plotwin = None            # used by plot_data()
    plot_trace = []
    border = 5            # used by window() etc.
    root = None
    line_data = []
    line_trace = []
    box_trace = []
    box_data = []
    grid_trace = []
    bordcol = '#555555'
    gridcol = '#f0f0f0'
    gridcol2 ='#d0d0d0'

                    
    def __init__(self, dev = None):
        """
        Dummy Phm. Returns zeros on reads. Swallows the writes
        """
        global logfile
        self.handle = 1
        return

# -------------------------- Digital I/O ---------------------------
    def read_inputs(self):
        return 0

    def read_acomp(self):
        return 0

    def write_outputs(self, val):
        return

    def pulse_out(self, data):
        return

#-------------------- Analog Outputs / Inputs ---------------------------

    def set_voltage(self, val):
        return

    def set_dac(self, val):
        return

    def select_adc(self, val):
        return

    def set_adc_size(self, val):
        self.adc_size = val
        return

    def zero_to_5000(self):
        return (0., 0.)
        
    def get_voltage(self):
        return (0.,0.)

    def minus5000_to_5000(self):
        return (0.,0.)

    def get_voltage_bip(self):
        return (0.,0.)

    def read_adc(self):
        return (0.,0)
        
    def adc_input_period(self, ch):
        return 0.

    def read_block(self, np, delay, bip=0):
        dat = []
        for i in range(np):
            dat.append([0.,0.])
        return dat

    def multi_read_block(self, np, delay, bip=0):
        dat = []
        index = 0
        for i in range(np):
                item = []
                item.append(i * self.adc_delay*nc) # *nc added 8-Sep-07
                for chan in range(self.num_chans):
                    item.append(0.)
                dat.append(item)
        return dat

    def add_channel(self, val):
        return
        
    def del_channel(self, val):
        return
        
    def get_chanmask(self):
        return   1

    def set_adc_trig(self, tr1, tr2, shifted = 0):
        return 0
        
    def enable_rising_wait(self, pin):
        return 0

    def enable_wait_high(self, pin):
        return 0

    def enable_falling_wait(self, pin):
        return 0

    def enable_wait_low(self, pin):
        return

    def disable_wait(self):
        return

    def enable_set_high(self, pin):
        return

    def enable_set_low(self, pin):
        return
        
    def enable_pulse_high(self, pin):
        return
        
    def enable_pulse_low(self, pin):
        return

    def disable_set(self):
        return

    def set_num_samples(self, val):
        self.num_samples = val
        return val

    def set_adc_delay(self, val):
        self.adc_delay = val
        return

    def set_frequency(self, freq):        # Freq in Hertz
        return 0

    def load_wavetable(self, v):
        return len(v)

    def start_wave(self, freq, plugin = 0):
        return 1.

    def pulse_d0d1(self, freq):
        return  1.0

    def stop_wave(self):
        return
        
    def measure_frequency(self):    # Returns freqency in Hertz
        return 0

#------------------------Time Interval Measurement routines-------------

    def r2ftime(self, pin1, pin2):
        return 1.0

    def r2rtime(self, pin1, pin2):
        return 1.0

    def f2rtime(self, pin1, pin2):
        return 1.0

    def f2ftime(self, pin1, pin2):
        return 1.0

    def multi_r2rtime(self, pin , skipcycles=0):
        return 1.0

    def pendulum_period(self, pin):
        return 1.0

    def set2rtime(self, pin1, pin2):
        return 1.0

    def set2ftime(self, pin1, pin2):
        return 1.0

    def clr2rtime(self, pin1, pin2):
        return 1.0

    def clr2ftime(self, pin1, pin2):
        return 1.0

    def pulse2rtime(self, tx, rx):
        return 1.0

    def pulse2ftime(self, tx, rx):
        return 1.0

    def set_pulse_width(self, width):
        return
        
    def set_pulse_polarity(self, pol):
        return

#-------------- Routines for the Radiation detection plug-in module.-------------

    def start_hist(self):
        return

    def stop_hist(self):
        return
        
    def clear_hist(self):
        return

    def read_hist(self):
        dat = []
        index = 0
        for i in range(256):
            dat.append((i,0))
        return dat

# --------------------- Devices on the Front Panel Slot --------------------

    def init_LCD_display(self):
        return
        
    def write_LCD(self, ch):
        return

    def message_LCD(self, msg):
        return
        
#----------------High Resolution ADC/DAC plug-in modules---------------
    hradc_initialized = False
    Vref = 2500.140		# reference in millivolts
    Rmask = 7
    RMAX  = 7			# maximum value of range is 7 (2.56V)
    hrchan = 0
    Gains = [128.0, 64.0, 32.0, 16.0, 8.0, 4.0, 2.0, 1.0]
    HRMAXCHAN = 15
    
    def hr_adc_init(self):
        return
        
    def hr_select_adc(self, chan):
        return

    def hr_select_range(self, val):
        return
        
    def hr_internal_cal(self, chan):
        return (0.,0.)

    def hr_external_cal(self, chan, zorfs):  # Zero or FS calib on chan
        return (0,0)

    def hr_read_adc(self):
        return (1.,0.)

    def hr_get_voltage(self):
        return (1., 0.)

        
#----------------------------- SPI 16 bit DAC ------------------------
    def hr_set_dac(self, val):
        return

    def hr_set_voltage(self, val):
        return

# --------------------- SEEPROM Pluin ------------------------------

    def seeprom_read(self, addr, nbytes):
        """
        Usage:
            s = phm()
        """
        v = []
        for k in range(nbytes):
            v.append(0)     
        return v

    def copy_eep2seep(self, addr):
        return

    def seeprom_verify(self, blocknum, data):
        return self.seeprom_read(addr, 128)

    def pmrb_get_data(self):
        return 0


#---------- World Coordinate Graphics Routines using Tkinter ------------

    def plot(self, data, width=400, height=300, parent = None):
        """
        Plots the result of read_block() functions. Provides Grid,
        window resizing and coordinate measurement.
        Multiple traces in case of multi_read_block() results.
        Will delete all the previous plots existing on the window.
        usage:
            v = p.read_block(200,10,1)
            p.plot(v, 400, 300)
        """
        if self.root == None:
            self.window(width,height,parent)
        self.remove_lines()
        self.xmax = data[-1][0]
        self.set_scale(self.xmin, self.ymin, self.xmax, self.ymax) 
        numchans = len(data[0]) - 1
        npoints = len(data)
        for ch in range(numchans):
            points = []
            for i in range(npoints):
                points.append((data[i][0], data[i][ch+1]))
            self.line(points, self.colors[ch])
        
# The simple window to plot Data returned by read_block() functions
    def plot_data(self,v):
        """
        Simple plot window that can be updated very fast.
        No grid or resize like plot()
        """
        if self.plotwin == None:
            self.plotwin = Tk()
            self.plotwin.title('Phoenix plot')
            self.plotwin.protocol("WM_DELETE_WINDOW", self.clean_qplot)
            self.canvas = Canvas(self.plotwin, background='white', width=WIDTH + 20, height=HALF_HEIGHT*2 + 20)
            self.canvas.pack()

            self.canvas.create_rectangle(10, 10, WIDTH+10, HALF_HEIGHT*2 + 10, outline='#009900')
            self.canvas.create_line([(10, HALF_HEIGHT+10), (WIDTH+10, HALF_HEIGHT+10)], fill='#00ff00')
        if len(self.plot_trace) != 0:
            map(lambda x: self.canvas.delete(x), self.plot_trace)
            self.plot_trace = []
            self.plotwin.update()
                    
        numchans = len(v[0]) - 1
        npoints = len(v)
        xscale = WIDTH/v[-1][0]
        yscale = HALF_HEIGHT/YMAX
        for ch in range(numchans):
            a = []
            for i in range(npoints):
                x = 10 + v[i][0] * xscale
                y = (HALF_HEIGHT + 10) - v[i][ch+1] * yscale
                a.append((x, y))
            line = self.canvas.create_line(a, fill=self.colors[ch])            
            self.plot_trace.append(line)
        self.plotwin.update()

    def window(self, width=400, height=300, parent = None):
        """
        Opens a Tkinter window. If no parent window given, a new root window
        is created and used as the parent.
        """
        from Tkinter import *
        if self.root == None:    # create a new window
            if parent == None:
                self.root = Tk()    # Inside Toplevel
                self.root.title('Phoenix plot')
            else:
                self.root = parent    # Inside the given parent window
            self.SCX = width
            self.SCY = height
            self.set_scale(0., -5000., 1000., 5000.) # temporary scale
        self.XLIM = width + 2 * self.border
        self.YLIM = height + 2 * self.border
        self.canvas = Canvas(self.root, background="white",\
        width = self.XLIM, height = self.YLIM)
        self.canvas.pack(expand = 1, fill = BOTH)
        self.canvas.bind("<Button-1>", self.show_xy)
        self.canvas.bind("<Button-3>", self.show_xy)
        self.root.bind("<Configure>", self.resize)
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

    def set_scale(self, x1, y1, x2, y2):
        """
        Calculate the scale factors to be used by draw functions from the
        upper and lower limits of the X and Y coordinates to be plotted.
        usage
            p.set_scale(xmin, ymin, xmax, ymax)
        """
        self.xmin = float(x1)
        self.ymin = float(y1)
        self.xmax = float(x2)
        self.ymax = float(y2)
        self.xscale = (self.xmax - self.xmin) / (self.SCX)
        self.yscale = (self.ymax - self.ymin) / (self.SCY)
        
    def auto_scale(self, data):
        xmin = data[0][0]
        xmax = data[-1][0]
        ymin = 1.0e10
        ymax = 1.0e-10
        for k in range(len(data)):
            if data[k][1] > ymax: ymax = data[k][1]
            if data[k][1] < ymin: ymin = data[k][1]
        self.set_scale(xmin,ymin,xmax,ymax*1.1)
     
    def w2s(self, p): #change from world to screen coordinates
        ip = []
        for xy in p:
            ix = self.border + int( (xy[0] - self.xmin) / self.xscale)
            iy = self.border + int( (xy[1] - self.ymin) / self.yscale)
            iy = self.YLIM - iy
            ip.append((ix,iy))
        return ip

    def box(self, points, col = '#e0e0e0'):
        """
        Draws a rectangle on the window opened earlier. Accepts a list
        of coordinate pairs.
        usage:
            p.box([(x1,y1),....,(xn,yn)], 'red')
        """
        ip = self.w2s(points)
        t = self.canvas.create_rectangle(ip, fill=col)
        self.box_trace.append(t)
        self.box_data.append((points, col))

    def remove_boxes(self):           
        for ch in range(len(self.box_trace)):
            self.canvas.delete(self.box_trace[ch])
        self.box_trace = []
        self.box_data = []

    def line(self, points, col = 'black', grid = 0):
        """
        Draws a line on the window opened earlier. Accepts a list
        of coordinate pairs.
        usage:
            p.line([(x1,y1),....,(xn,yn)], 'red')
        """
        ip = self.w2s(points)
        t = self.canvas.create_line(ip, fill=col, smooth = 0)
        if grid == 0:
            self.line_trace.append(t)
            self.line_data.append((points, col))
        else:
            self.grid_trace.append(t)


    def remove_lines(self):
        """
        Deletes all the lines drawn by functions line() and plot()
        """
        for ch in range(len(self.line_trace)):
            self.canvas.delete(self.line_trace[ch])
        self.line_trace = []
        self.line_data = []
    
    def draw_grid(self):
        major = 10
        minor = 100
        dx = (self.xmax - self.xmin) / major
        dy = (self.ymax - self.ymin) / major
            
        x = self.xmin
        while x <= self.xmax:
            self.line([(x,self.ymin),(x,self.ymax)],self.gridcol,1)
            x = x +dx
        y = self.ymin
        while y <= self.ymax:
            self.line([(self.xmin,y),(self.xmax,y)],self.gridcol,1)
            y = y +dy

        dx = (self.xmax - self.xmin) / minor
        dy = (self.ymax - self.ymin) / minor
        x = self.xmin
        while x <= self.xmax:
            self.line([(x, 0.),(x, dy)],self.gridcol2,1)
            x = x +dx
        y = self.ymin
        while y <= self.ymax:
            self.line([(0., y),(dx,y)],self.gridcol2,1)
            y = y +dy

    def close_window(self):
        self.root.destroy()
        self.root = None

    def resize(self, event):
        if event.widget != self.canvas:
            return
        self.SCX = event.width - 2 * (self.border+1)
        self.SCY = event.height - 2 * (self.border+1)
        self.XLIM = event.width
        self.YLIM = event.height
        self.set_scale(self.xmin, self.ymin, self.xmax, self.ymax)    
        for ch in range(len(self.grid_trace)):
            self.canvas.delete(self.grid_trace[ch])
        self.grid_trace = []
        self.draw_grid()

        for ch in range(len(self.line_trace)):
            self.canvas.delete(self.line_trace[ch])
            ip = self.w2s(self.line_data[ch][0])
            col = self.line_data[ch][1]
            self.line_trace[ch] = self.canvas.create_line(ip, fill=col)

    marker = None
    def show_xy(self,event):
        """
            Prints the XY coordinated of the current cursor position
        """
        ix = self.canvas.canvasx(event.x) - self.border
        iy = self.YLIM - self.canvas.canvasy(event.y) - self.border
        x = ix * self.xscale + self.xmin
        y = iy * self.yscale + self.ymin

        s = None
        if event.num == 1:
            s = 'x = %5.0f\ny = %5.3f' % (x,y)
            self.marker = (x,y)
        elif event.num == 3 and self.marker != None:
            s = 'x = %5.0f  dx = %5.0f\ny = %5.3f  dy = %5.3f' % \
            (self.marker[0], x-self.marker[0], self.marker[1], y - self.marker[1])
        try:
            self.canvas.delete(self.xydisp)
        except:
            pass
        if s != None: 	 
            self.xydisp = self.canvas.create_text(self.border+1,self.SCY-1, \
            anchor = SW, justify = LEFT, text = s)

    def clean_qplot(self):
        self.plotwin.destroy()
        self.plotwin = None
        self.trace = []

    def save_data(self, v, fn = 'plot.dat'):
        """
        Saves the dataset returned by read_block() functions
        to a file in multi-column format
        default filename is 'plot.dat'
        Usage:
            v = p.read_block(200,10,1)
            p.save_data(v, 'myfile.dat')
        """
        f = open(fn,'w')
        numchans = len(v[0]) - 1
        npoints = len(v)
        for x in v:
            s = ''
            for i in x:
                s = s + str(i) + ' '
            s = s + '\n'
            f.write(s)
        f.close()


#---------Functions to send PC time stamp to Phoenix and read UC time-----------

    def set_time(self):
        return 0
        
    def get_time(self):
        return 0

#----------------------SLOW Multi Read Block functions -------------------------
    def smrb_start(self, np, delay,bip):
        return 0
        
    def smrb_status(self):
        return 0
        
    def smrb_getdata(self):
        return 0

    def pmrb_start(self, np, delay):
        return 0

    def pmrb_running(self):
        return 0

    def eeprom_write_byte(self,addr, dat):
        return

    def get_mcustatus(self):
        return

    def get_version(self):
        return 'OL'

    def chip_enable(self, dev):
        return 0

    def chip_enable_bar(self, dev):
        return 0

    def spi_push(self, dat):
        return 0

    def spi_push_bar(self, dat):
        return 0

    def spi_pull(self):
        return 0

    def spi_pull_bar(self):
        return 0

    def chip_disable(self):
        return

    def gm_get_count(self, dur=1):
        return 0
        
    def gm_get_voltage(self):
        return 0
        
    def gm_set_voltage(self,tv):
        return tv

