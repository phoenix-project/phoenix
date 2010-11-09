from Tkinter import *
import Image, ImageTk, ImageDraw, os, commands
import phm, time
from utils import Data, abs_path

photograph = 'panel.jpg'

class explore:
    NP = 100
    adc_delay = 10
    delay_vals = [10,20,50,100,200,500,1000]
    numchans = 1
    xlabel = 'milli seconds'
    ylabel = 'Volts'
    bw = ['black', 'white']	
    by = ['black', 'yellow']	
    br = ['black', 'red']	
    size = [350.0, 272.0]
    dotdx = 0.012
    dotdy = 0.015
    delta	= 0.03
    playing_tune = False

    # adc info [x, y, canvas_oval, status, color, coordinate data list]
    adcs  = [[0.620, 0.717, None, 0, 'black', [] ],\
             [0.620, 0.621, None, 0, 'red'  , [] ],\
             [0.620, 0.523, None, 0, 'green', [] ],\
             [0.620, 0.432, None, 0, 'blue',  [] ] ]

    #Digital have x,y,oval & value
    douts = [[0.21, 0.739, None, 0],\
         [0.286, 0.739, None, 0],\
         [0.360, 0.739, None, 0],\
         [0.434, 0.739, None, 0]]

    dins = [[0.212, 0.836, None, 0],\
         [0.285, 0.836, None, 0],\
         [0.359, 0.836, None, 0],\
         [0.433, 0.836, None, 0]]
         
    cmp   = [0.508, 0.432, None, 0]

    digin_data = 0		# will force the first update 
    cmp_stat = 0		# Comparator status	
         
    ccs   = [0.335, 0.246]
    led   = [0.245, 0.339, None, 0]	# x, y, oval & status
    dc5v  = [0.333, 0.342, None, 0]
    # DAC, CNTR & PWG has x, y, oval, status & value fields
    dac   = [0.434, 0.337, None, 0, 0.0]
    cntr  = [0.333, 0.431, None, 0, 0.0]
    pwg   = [0.433, 0.431, None, 0, 1000.0] # 1000 Hz 

    ls_ins = [[0.841, 0.715, None, 0],\
             [0.840, 0.620, None, 0]]
    ls_outs= [[0.701, 0.715],\
         [0.701, 0.619]]

    ia_in = [[0.615, 0.245],\
         [0.615, 0.33]]
    ia_out= [[0.838, 0.240],\
         [0.838, 0.337]]
    ia_gb = [[0.689, 0.243],\
         [0.689, 0.339]]
    ia_ge= [[0.763, 0.242],\
         [0.763, 0.337]]

    nia_in = [0.916, 0.830]
    nia_out= [0.916, 0.620]
    nia_gb = [0.702, 0.833]
    nia_ge = [0.841, 0.833]

    gnds = [[0.911, 0.242],[0.940, 0.339], [0.508, 0.738], [0.508, 0.834]]

    adctl   = [0.62,0.85]   # Text display of ADC outputs
    dispadc = False
    adctext = [0,0,0,0]
    adcbox  = [0,0,0,0]

    ph = None		# The phoenix handler set by main program
    plot2d = None	# The 2D plot window
    msgwin = None	# The message window
    adc_scale = None  
     

    def __init__(self, parent, size, plot, msg):
        self.parent = parent
        self.plot2d = plot
        self.msgwin = msg
        self.data = Data()
                
        x = Image.open(abs_path(photograph))	# Images are kept along with the python code
        im = x.resize(size)        

        self.size[0] = float(im.size[0])
        self.size[1] = float(im.size[1])
        self.image = ImageTk.PhotoImage(im)
        self.canvas = Canvas(parent, width = im.size[0], height = im.size[1])
        self.canvas.create_image(0,0,image = self.image, anchor = NW)

	self.adblock = self.canvas.create_rectangle(self.dotxy(self.adctl),fill='white')
        
        for k in self.douts:
            k[2] = self.canvas.create_oval(self.dotxy(k), outline="", fill = 'black')
        for k in self.dins:
            k[2] = self.canvas.create_oval(self.dotxy(k), outline="", fill = 'black')
        for k in self.adcs:
            k[2] = self.canvas.create_oval(self.dotxy(k), outline="", fill = 'black')
        for k in self.ls_ins:
            k[2] = self.canvas.create_oval(self.dotxy(k), outline="", fill = 'black')
        self.led[2] = self.canvas.create_oval(self.dotxy(self.led), outline="", fill = 'black')
        self.pwg[2] = self.canvas.create_oval(self.dotxy(self.pwg), outline="", fill = 'black')
        self.dac[2] = self.canvas.create_oval(self.dotxy(self.dac), outline="", fill = 'black')
        self.cntr[2] = self.canvas.create_oval(self.dotxy(self.cntr), outline="", fill = 'black')
        self.cmp[2] = self.canvas.create_oval(self.dotxy(self.cmp), outline="", fill = 'black')
        self.canvas.bind("<ButtonRelease-1>", self.mouse_click)
        self.canvas.pack()    

    def enter(self, fd):	# Called when entering this expt
        self.msg_intro()
        self.canvas.itemconfigure(self.led[2],  fill = 'red')
        for adc in self.adcs:			# initialize ADC data
            adc[3] = 0
            self.canvas.itemconfigure(adc[2],fill = 'black')
            adc[5] = []
            for xy in range(self.NP):
                adc[5].append( (0.0, 0.0) ) 
        self.updating = True
        self.plot2d.setWorld(0, -5, self.NP * self.adc_delay/1000.0, 5)
        self.plot2d.mark_axes(self.xlabel,self.ylabel,self.numchans)

        self.ph = fd
        try:
            self.ph.set_frequency(1000)
            for ch in range(4):
                self.ph.del_channel(ch)
        except:
            self.msgwin.msg('Connection NOT established', 'red')
            
    def exit(self):			# Clear popup etc. here
        self.updating = False
#        if self.playing_tune == True:
          
        

    def set_adc_delay(self,w):
        d = self.adc_scale.get()    
        self.adc_delay = self.delay_vals[d]
        if self.ph == None:
            return
        self.ph.set_adc_delay(self.adc_delay)
        self.plot2d.setWorld(0, -5, self.NP * self.adc_delay/1000.0, 5)
        self.plot2d.mark_axes(self.xlabel,self.ylabel,self.numchans)
        
    def calc_numchans(self):
        self.numchans = 0
        for k in self.adcs:
            if k[3] == 1:
                self.numchans = self.numchans  + 1
        self.set_adc_delay(None)   	
#--------------------------------------------------------------------
    def w2s(self,x,y):		#world to screen coordinates
	return x*self.size[0], y*self.size[1]

    def dotxy(self,socket):
        x1 = self.size[0] * (socket[0] - self.dotdx)
        y1 = self.size[1] * (socket[1] - self.dotdy)
        x2 = self.size[0] * (socket[0] + self.dotdx)
        y2 = self.size[1] * (socket[1] + self.dotdy)
        return(x1,y1,x2,y2)

    def set_pwg(self,w):
        freq = self.pwg_scale.get()
        f = float(freq)
        self.pwg[4] = self.ph.set_frequency(f)
        s = '%3.1f Hz'%(self.pwg[4])
        self.pwg_label.config(text=s)

    def add_pwg(self):
        self.pwg_frame = Frame()    
        self.pwg_scale =  Scale(self.pwg_frame, command = self.set_pwg, from_ = 0,\
		to=10000, orient=HORIZONTAL, length=100, showvalue=0)
        self.pwg_scale.set(self.pwg[4])
        self.pwg_scale.pack(side=TOP)
        self.pwg_label = Label(self.pwg_frame)
        self.pwg_label.pack(side=TOP)

        xc = self.size[0] * self.pwg[0] + 10
        yc = self.size[1] * self.pwg[1] + 10
        self.canvas.create_window(int(xc), int(yc), \
        anchor = NW, window = self.pwg_frame)

    def remove_pwg(self):
        self.canvas.itemconfigure(self.pwg[2],  fill = 'black')
        self.pwg_label.destroy()
        self.pwg_scale.destroy()
        self.pwg_frame.destroy()

#----------------------- DAC Control ------------------------       
    def set_dac(self,w):
        mv = self.dac_scale.get()
        self.dac[4] = float(mv)
        self.ph.set_voltage(self.dac[4])
        s = '%4.0f mV'%(self.dac[4])
        self.dac_label.config(text=s)

    def add_dac(self):
        self.dac_frame = Frame()    
        self.dac_scale =  Scale(self.dac_frame, command = self.set_dac, from_ = 0,\
		to=5000, orient=HORIZONTAL, length=100, showvalue=0)
        self.dac_scale.set(self.dac[4])
        self.dac_scale.pack(side=TOP)
        self.dac_label = Label(self.dac_frame)
        self.dac_label.pack(side=TOP)

        xc = self.size[0] * self.dac[0] + 10
        yc = self.size[1] * self.dac[1] + 10
        self.canvas.create_window(int(xc), int(yc), anchor = NE, \
            window = self.dac_frame)
        self.canvas.itemconfigure(self.dac[2],  fill = 'white')
        self.dac[3] = 1
    
    def remove_dac(self):
        self.dac_label.destroy()
        self.dac_scale.destroy()
        self.dac_frame.destroy()
        self.canvas.itemconfigure(self.dac[2],  fill = 'black')
        self.dac[3] = 0
    
#----------------------- CNTR Reading  ------------------------       
    def get_cntr(self):
        self.cntr[4] = self.ph.measure_frequency()
        s = '%4.0f Hz'%(self.cntr[4])
        self.cntr_value.set(s)

    def add_cntr(self):
        self.cntr_frame = Frame()    
        self.cntr_value = StringVar()
        self.cntr_value.set('0.0 Hz')
        self.cntr_button =  Button(self.cntr_frame, \
            textvariable = self.cntr_value, command = self.get_cntr)
        self.cntr_button.pack(side=TOP)
        xc = self.size[0] * self.cntr[0] + 10
        yc = self.size[1] * self.cntr[1] + 10
        self.canvas.create_window(int(xc), int(yc), anchor = NE,\
             window = self.cntr_frame)
        self.canvas.pack()
        self.get_cntr()
    
    def remove_cntr(self):
        self.cntr_button.destroy()
        self.cntr_frame.destroy()
        self.canvas.itemconfigure(self.cntr[2],  fill = 'black')
        self.cntr[3] = 0

#-------------------------------------------------------------
    def selected(self, socket, e):
        if abs(e.x / self.size[0] - socket[0]) < 0.03 and \
                abs(e.y / self.size[1] - socket[1]) < 0.03:
            return True
        return False
  
    def mouse_click(self, e):	# Runs when user clicks on the Photograph
        self.msg_intro()
        if self.ph == None:
            self.msgwin.msg('Connection NOT established', 'red')
            return

        if self.selected(self.adctl,e):
            self.msg_adcdisp()
            if self.dispadc == False:
                self.dispadc = True
                self.canvas.itemconfigure(self.adblock,fill='yellow')
                for i in range(4):
                    tl = self.w2s(0.65, self.adcs[i][1] - .03)
                    rb = self.w2s(0.76, self.adcs[i][1] + .03)
                    self.adcbox[i] = self.canvas.create_rectangle(tl[0], tl[1], rb[0], rb[1], fill = 'white')
                    txy = self.w2s(0.655, self.adcs[i][1])
                    self.adctext[i] = self.canvas.create_text(txy, text = 'TEXT', fill = 'black', anchor = 'w')
            else:
                self.dispadc = False
                self.canvas.itemconfigure(self.adblock,fill='white')
                for i in range(4):
                      self.canvas.delete(self.adcbox[i])
                      self.canvas.delete(self.adctext[i])
            return

        for k in range(4):			# ADC Inputs
            if self.selected(self.adcs[k], e):
              self.msg_adc()
              if self.adcs[k][3] == 0:		# Not selected
                self.adcs[k][3] = 1		# Add trace
                self.calc_numchans()
                self.canvas.itemconfigure(self.adcs[k][2], fill = 'white')
                self.ph.add_channel(k)
              else:
                self.adcs[k][3] = 0	# Remove trace
                self.calc_numchans()
                self.canvas.itemconfigure(self.adcs[k][2], fill = 'black')
                self.ph.del_channel(k)

        for ls in self.ls_ins:			# Level Shifters
            if self.selected(ls, e):
                  self.msg_adc()
                  ls[3] = ~ls[3] & 1		# Toggle status
                  self.canvas.itemconfigure(ls[2],fill = self.bw[ls[3]] )

        if self.selected(self.pwg, e):		# PWG
            self.msg_pwg()
            if self.dac[3] == 1:		# Either DAC or PWG at a time
                self.msgwin.msg('Remove DAC to use PWG','red')
                return
            if self.pwg[3] == 1:
                self.pwg[3] = 0
                self.remove_pwg()
            else:
                self.add_pwg()
                self.pwg[3] = 1
            self.canvas.itemconfigure(self.pwg[2], fill = self.bw[self.pwg[3]])
            
        if self.selected(self.dac, e):		# DAC
            self.msg_dac()
            if self.pwg[3] == 1:
                self.msgwin.msg( 'Remove PWG to use DAC','red')
                return
            if self.dac[3] == 1:
                self.dac[3] = 0
                self.remove_dac()
            else:
                self.add_dac()
                self.dac[3] = 1
            self.canvas.itemconfigure(self.dac[2], \
                fill = self.bw[self.dac[3]])

        if self.selected(self.cntr, e):		# CNTR
            self.msg_cntr()
            if self.cntr[3] == 1:
                self.cntr[3] = 0
                self.remove_cntr()
            else:
                self.cntr[3] = 1
                self.add_cntr()
            self.canvas.itemconfigure(self.cntr[2],\
                fill = self.bw[self.cntr[3]])

        data = 0			# Digital Outputs
        for k in range(4):	
            if self.selected(self.douts[k], e):
                self.douts[k][3] = (~self.douts[k][3]) & 1	# Toggle status
                self.msg_douts()
                self.canvas.itemconfigure(self.douts[k][2],\
                  fill = self.br[self.douts[k][3]] )
                self.msgwin.showtext('\nYou just toggled D%d'%(k))
            data = data | (self.douts[k][3] << k)        
        self.ph.write_outputs(data)
    

        for k in range(4):			# Digital Inputs
            if self.selected(self.dins[k], e):
                self.msg_dins()
                tp = self.ph.multi_r2rtime(k,99)
                if tp > 0:
                  fr = 1.0e8/tp
                else:
                  fr = 0.0
                self.msgwin.showtext('\nFrequency = %5.2f Hz'%(fr))

        if self.selected(self.cmp, e):
            self.msg_cmp()
            tp = self.ph.multi_r2rtime(4,99)
            if tp > 0:
              fr = 1.0e8/tp
            else:
              fr = 0.0
            self.msgwin.showtext('\nFrequency = %5.2f Hz'%(fr))

# No action other than help message required for the following items

        if self.selected(self.ccs, e):
            self.msg_ccs()

        if self.selected(self.dc5v, e):
            self.msg_dc5v()


        for k in range(2):			# Inverting Amps
            if self.selected(self.ia_in[k], e) or \
               self.selected(self.ia_out[k], e) or \
               self.selected(self.ia_gb[k], e) or \
               self.selected(self.ia_ge[k], e):
                 self.msg_ia()

                                               # Non Inverting amp
        if self.selected(self.nia_in, e) or \
               self.selected(self.nia_out, e) or \
               self.selected(self.nia_gb, e) or \
               self.selected(self.nia_ge, e):
                 self.msg_nia()
        
        for k in range(4):			# GND Sockets
            if self.selected(self.gnds[k], e):
                self.msg_gnds()
        
        self.canvas.pack()	
#---------------------Panel Click action ends here-----------------

    def update(self):
        try:
            data = self.ph.read_inputs() & 15	# Digital Inputs
        except:
            self.msgwin.msg('Connection NOT established', 'red')

        if self.dispadc == True:
            for i in range(2): 
                self.ph.select_adc(i)
                if self.ls_ins[i][3]:
                   ss = '%4.2f V'%(self.ph.get_voltage_bip()[1]*0.001)
                else:
                   ss = '%4.2f V'%(self.ph.get_voltage()[1]*0.001)
                self.canvas.itemconfigure(self.adctext[i],text = ss)
            for i in range(2,4): 
                self.ph.select_adc(i)
                ss = '%4.2f V'%(self.ph.get_voltage()[1]*0.001)
                self.canvas.itemconfigure(self.adctext[i],text = ss)

        if data != self.digin_data:
            self.digin_data = data
            for k in range(4):	
                self.canvas.itemconfigure(self.dins[k][2],  \
                fill = self.by[(data >> k) & 1])
            self.canvas.pack()
            
            
        cs = ~self.ph.read_acomp() & 1	# returns 1 when socket if < 1.23 V 
        if cs != self.cmp_stat:
            self.cmp_stat = cs 
            self.canvas.itemconfigure(self.cmp[2], fill = self.by[cs])
            self.canvas.pack()

        if self.updating == False:  return
          
        have_work = False
        for k in self.adcs:
          if k[3] == 1:
            have_work = True
 
        if have_work == False:	# No channels selected
          return

        try:
          self.phdata = self.ph.multi_read_block(self.NP, self.adc_delay, 0)
          if self.phdata == None:
                return
        except:
          return
 
        ch = 0;
        for k in range(4):			# Copy data to traces
            adc = self.adcs[k]
            if self.adcs[k][3] == 1:		# Active channel
                if k < 2:			# CH0 or CH1
                    for xy in range(self.NP):
	                if self.ls_ins[k][3] == 0:	# No Level Shifter
    		            self.adcs[k][5][xy] = (self.phdata[xy][0]/1000.0,\
                               self.phdata[xy][ch+1]/1000.0 )
                        else:
    		            self.adcs[k][5][xy] = (self.phdata[xy][0]/1000.0, \
    		              5.0 - 2.0 * self.phdata[xy][ch+1]/1000.0 )
                else:
	            for xy in range(self.NP):
    		            self.adcs[k][5][xy] = (self.phdata[xy][0]/1000.0,\
                               self.phdata[xy][ch+1]/1000.0)
                ch = ch + 1
        
        self.plot2d.delete_lines()
        for adc in self.adcs:
            if adc[3] == 1:			# Active channel
                self.plot2d.line(adc[5], adc[4])
  
#-----------------------------------------------------------------------
    def start(self,e):
        self.updating = True

    def stop(self,e):
        self.updating = False

    def save_all(self,e):
        fname = self.fntext.get()
        if fname == None:
          return
        self.data.traces = []
        for adc in self.adcs:
            if adc[3] == 1:			# Active channel
              self.data.traces.append(adc[5])
        self.data.save_all(fname)
        self.msgwin.msg('Data saved to '+ fname)

#-------------------------- Message routines -------------
    def msg_intro(self):
        self.msgwin.clear()
        self.msgwin.showtext('This section helps you to explore ' +\
          'the different building blocks of PHOENIX. ')
        self.msgwin.showtext('Click on the different Sockets ', 'blue')
        self.msgwin.showtext('shown in  the Photograph to explore the system. '+\
        'Select "Connect" from the main before proceeding.\n'+\
        'From here you can use Phoenix as a test equipment also. The ADC '+\
        'inputs acts like CRO inputs. Digital Inputs can measure frequency '+\
        'of the 0-5V range signals etc.')
    def msg_ccs(self):
        self.msgwin.clear()
        self.msgwin.showtext('This socket gives a constant current of 1 mA ' +\
          'to load resistors upto 1KOhm. This feature is mainly used for ' +\
          'temperature measurements using RTD sensor elements.')

    def msg_cmp(self):
        self.msgwin.clear()
        self.msgwin.showtext('This is one of the Inputs of an Analog ' +\
          'Comparator. The other input is internally connected to around ' +\
          '1.2 V. Connect the DAC output to CMP input and change the DAC ' +\
          'slider to see how it works. Similar to Digital Input Sockets ' +\
          'the CMP input also is used for time interval measurements. '+\
          'Clicking on CMP Socket will try to measure the '+\
          'frequency of the signal at the input. If nothing is connected '+\
          'the message will be displayed after the timeout and you will '+\
          'notice a delay.')

    def msg_dc5v(self):
        self.msgwin.clear()
        self.msgwin.showtext('Phoenix is powered by an unregulated 9V DC ' +\
          'supply which is regulated inside. The 5V DC output is available ' +\
          'on the Panel. This can only supply around 100 mA of current.')

    def msg_pwg(self):
        self.msgwin.clear()
        self.msgwin.showtext('The Programmable Waveform Generator ' +\
          'gives a square wave output. Frequency can be varied '+\
          'between 13 Hz and 10 KHz using the slider. ' +\
          'ou cannot set it to all the Using the set_frequency() '+\
          'function in the Phoenix library you can set it up to 4 MHz.'+\
          'The voltage level swings between 0 and 5V. To view this ' +\
          'waveform connect a wire from PWG to CH0 and click on CH0 to ' +\
          'add that channel to the plot window. Move the slider and ' +\
          'see the result. Frequency cannot be set to all the values '+\
          'between the limits due to the nature of the hardware.\n\n')

        self.msgwin.showtext('You can play a tune on PWG. Connect the '+\
        'Loudspeaker from PWG to Ground (with 100 Ohm series resisitor).\n'+\
        'Quit this and run /docs/phoenix/applications/TerminalProgs/jan.py')

    def msg_dac(self):
        self.msgwin.clear()
        self.msgwin.showtext('The DAC socket can be programmed to give ' +\
          'a DC voltage between 0 to 5V. The DAC us implemented using ' +\
          'Pulse Width Modulation technique. In fact the DAC socket is ' +\
          'the PWG socket output filtered. When in DAC mode the PWG will ' +\
          'show a 31.25 KHz squarewave whose duty cycle varies with the '+\
          'DAC voltage setting. Due to this reason, you can only use PWG '+\
          'or DAC at a time.')

    def msg_cntr(self):
        self.msgwin.clear()
        self.msgwin.showtext('Measures the frequency of the 5V signal ' +\
          'connected at the input. To test this feature, connect PWG output ' +\
          'to CNTR input using a cable and set PWG to some value. ' +\
          'CNTR can be updated by clicking on the currently displyed ' +\
          'frequency value.')

    def msg_douts(self):
        self.msgwin.clear()
        self.msgwin.showtext('The Digital Output Sockets can be made ' +\
          '0V or 5V under software control. Under this program, clicking ' +\
          'on a socket will toggle the state. The output D0 alone is' +\
          'transistor buffered to drive upto 100 mA. The rest can drive ' +\
          'only upto 5 mA ')

    def msg_dins(self):
        self.msgwin.clear()
        self.msgwin.showtext('The voltage level at the Digital Input sockets ' +\
          'can be read through software. This program makes the socket hole ' +\
          'Yellow if it is conencted to 0V, floating inputs are 5 Volts. ' +\
          'Connect one socket to GND using a cable and watch the picture above. ' +\
          'The time between voltage level transitions at Digital Input'+\
          'Sockets can be measured with microsecond accuracy. '+\
          'Clicking on a Digital input Socket will try to measure the '+\
          'frequency of the signal at the input. If nothing is connected '+\
          'the message will be displayed after the timeout and you will '+\
          'notice a delay.')


    def msg_ls(self):
        self.msgwin.clear()
        self.msgwin.showtext('Level Shifting Amplifiers convert a -5V to 5V ' +\
          'range signal to a 0 to 5V range signal. A 5V DC value is added ' +\
          'to the input signal and the amplitude is reduced to half. With ' +\
          'the input connected to GND, the output will be nearly 2.5 Volts.')


    def msg_ia(self):
        self.msgwin.clear()
        self.msgwin.showtext(' ' +\
          'The variable gain Inverting Amplifiers are implemented using '+\
          'TL084 op-amps. ' +\
          'The Feedback Resistor (Rf)is fixed at 10 KOhms. The Input Resistor ' +\
          '(Ri) can be changed by the user to adjust the gain. Remember that ' +\
          'TL084 Op-amps have around 2mV (multiply by the gain) offset. The '+\
          'Op-amps inside Phoenix are powered by a charge pump generating '+\
          '+8V and -7V supplies from +5V. The output of these amplifiers ' +\
          'saturate at nearly 5V due to this reason.')

    def msg_nia(self):
        self.msgwin.clear()
        self.msgwin.showtext(' ' +\
          'The variable gain Non-Inverting Amplifiers are implemented using '+\
          'LM358 op-amp, which is good only for low frequencies. ' +\
          'The Feedback Resistor (Rf)is fixed at 10 KOhms. The Gain Selection '+\
          ' Resistor (Rg) can be changed by the user to adjust the gain. '+\
          'Op-amps inside Phoenix are powered by a charge pump generating '+\
          '+8V and -7V supplies from +5V. The output of these amplifiers ' +\
          'saturate at nearly 5V due to this reason.')

    def msg_gnds(self):
        self.msgwin.clear()
        self.msgwin.showtext('These sockets are at zero volts. ')

    def msg_adcdisp(self):
        self.msgwin.clear()
        self.msgwin.showtext('Clicking on the white square below the ADC Inputs '+\
          'starts the display of voltages at the Analog inputs CH0 to CH3. '+\
          'Click again to stop displaying the voltage valeus.')

    def msg_adc(self):
        self.msgwin.clear()
        self.msgwin.showtext('The voltage input at the ADC input channels can be ' +\
          'read through software. They can be read at regular time intervals and ' +\
          'plotted to get the input waveform. Four channels are available. Clicking '+\
          'on the sockets will Enable/Disable scanning. The ADC inputs must be '+\
          'between 0 to 5V. However, CH0 and CH1 can be used with the level shifting '+\
          'amplifiers to display a -5V to 5V range signal. To display the voltage '+\
          'at the Level Shifter Input Socket click on it. The functions available are:\n')
        self.msgwin.showlink('Stop Scanning', self.stop)
        self.msgwin.showtext(' To stop updating.\n')
        self.msgwin.showlink('Save Traces', self.save_all)
        self.msgwin.showtext(' to save the data to text file named ') 
        self.fntext =  Entry(None, width =20, fg = 'red')
        self.msgwin.showwindow(self.fntext)
        self.fntext.insert(END,'cro.dat')
        self.msgwin.showtext('\n')
        self.msgwin.showlink('Start Scanning', self.start)
        self.msgwin.showtext('  To start updating again')
        self.msgwin.showtext('\nAdjust the time axis using the slider ')
        if self.adc_scale != None:
            self.adc_scale.destroy()
        self.adc_scale =  Scale(None, command = self.set_adc_delay, \
          from_ = 0, to=6, orient=HORIZONTAL, length=100, showvalue=0)
        for i in range(len(self.delay_vals)):
          if self.delay_vals[i] == self.adc_delay:
            self.adc_scale.set(i)
        self.msgwin.showwindow(self.adc_scale)
        self.msgwin.showtext('. What your are changing is the time interval '+\
         'between digitizations.')
        
