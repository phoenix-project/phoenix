import array, time, sys, os, struct
from math import *
from Tkinter import *   

"""
Python library for communicating to the "C program" on ATmega16 using RS232
interface. The commands are grouped according to the number of bytes should
follow as input data.
Each call to ATmega16 sends a status reply and variable length Data.
The Python function is responsible for receiving the correct amount of
data. No handshaking protocol is used at the moment.
There are some commands that initiate some periodic activity on ATmega16 and
collects the data later.

This library also has some Tkinter based graphics routins. The plot routines
Y-axis scale is assumed to be from -5000 to +5000. Can be improved

The UPhm class handles the communications through the ATmega8 based
USB version

Last Edited 30-Jun-09 : function usb_reconnect() added
    serial and usb modules are loaded only when required.
"""

#-----------------Commands to the kernel running on Atmaga16 ------------
# Commands with No arguments. ATmega16 starts action after getting a single byte (1 to 40)
LCD_INIT    =   1    # Clear LCD Display
DIGIN       =   2    # Digital Input (4 bits)
READBLOCK   =   3    # ADC read block
MULTIREADBLOCK =4    # ADC read block
ADCREAD     =   5    # Digitises selected channel
GETCHANMASK =   6    # Channel mask info for MRB
COUNT       =   7    # measure the frequency of counter input
READACOMP   =   8    # Analog comparator status, 1 when IN- < 1.23V
GETTIME     =   9    # get the time is seconds since Epoch
STARTHIST   =  10    # Start histogramming
READHIST    =  11    # Send the histogram to PC, 2 x 256 bytes data
CLEARHIST   =  12    # Clear the histogram memory
STOPHIST    =  13    # Stop histogramming
STOPWAVE    =  14    # Disable interrupt based waveform generation
SMRB_START  =  15    # Initiate an interrupt driven multi read block
SMRB_STATUS =  16    # Returns the TC0 ISR status + nbytes collected
SMRB_GETDATA=  17    # Sends the data collected by SMRB to PC
SMRB_STOP =    18    # Force Stop SMRB
PMRB_STATUS =  19    # Returns the TC0 ISR status
PMRB_GETDATA=  20    # Data collected in PROM by PMRB to PC
SPI_PULL    =  21    # Pull one byte from SPI
SPI_PULL_BAR=  22    # Pull for AD7718 like device
CHIP_DISABLE=  23    # CS disable for SPI
HR_ADCINIT  =  24    # SPI ADC
HRADCREAD   =  25    # Digitizes the addon ADC , current channel
GETMCUSTAT  =  26    # Get several microcontroller registers
GETVERSION  =  27    # Get the version information phx.y
HR_GET_CAL  =  28    # Read the AD7718 gain & offsetregisters

# Commands with One byte argument ( AT waits for one more byte before processing)(41 to 80)
DIGOUT     =   41    # Digital output (4 bits)
SETADCSIZE =   42    # ADC data size (1 or 2)
SETCURCHAN =   43    # Select Current ADC channel
R2FTIME    =   44    # Rise to Fall of signal on input pins
R2RTIME    =   45    # Rise to Fall of signal on input pins
F2RTIME    =   46    # Fall to Rise of signal on input pins
F2FTIME    =   47    # Fall to Rise of signal on input pins
SET2RTIME =    48    # Setting of bit to rising edge
SET2FTIME =    49    # to falling time
CLR2RTIME =    50    # Setting of bit to rising edge
CLR2FTIME =    51    # to falling time
PULSE2RTIME =  52    # Pulse to rising edge
PULSE2FTIME =  53    # Pulse to falling edge
SETPULSEWIDTH =54    # width for PULSE2 functions (0 to 250)
SETPULSEPOL =  55    # PULSE polarity (0 for HIGH true)
ADDCHAN =      56    # Add to MRB list 
DELCHAN =      57    # Del from "
SETDAC    =    58    # Set the PWM ADC (0 to 255) 0 to 5V
TPEND =        59    # Period og pendulum from light barrier
PULSEOUT =     60    # Send 100 pulses on D3, specify gap between them
AINPERIOD =    61    # measure ADC input signal periods
LCD_PUTCHAR =  62    # display to LCD
CHIP_ENABLE =  63    # Enable SPI device    
CHIP_ENABLE_BAR=64   # Enable SPI device    
SPI_PUSH  =    65    # Push one byte to SPI
SPI_PUSH_BAR = 66    # Push one byte to SPI
HR_SETCHAN =   67    # SPI ADC select channel
HR_CALINT =    68    # internal calibration of selected channel
HR_CALEXT =    69    # External Zero /FS calibration
GETPORT   =    70    # Read the uC port

# Commands with Two bytes argument (81 to 120)
SETNUMSAMPLES =81    # Number of samples per channel 
SETCOUNTER2  = 82    # Oscillator output on counter2
SETADCDELAY =  83    # Interval between digitizations ( 0 to 1000 usec)
SETACTION =    84    # Block Read Actions of SET/CLR type
WAITACTION =   85    # Block Read Actions of wait type
MULTIR2R =     86    # Rising edge to rising edge after N cycles
ADCTRIGLEVELS =87    # First and second ADC trigger level values
HRSETDAC =     88    # 16 bit DAC
SETWAVEFORM =  89    # We need to calculate OCR0, clock tick is 32 usec
PULSE_D0D1 =   90    # Interrupt driven square wave on D0 and D1
MULTI_EDGES =  91    # Rising and Falling Edge pair timings
COPY_E2S =     92    # copy eeprom to seeprom plugin, at specified address
SETDDR   =     93    # Set the direction of uC port
SETPORT  =     94    # Set Data/or pullup on uC port

# Commands with Three bytes argument (121 to 150)    
READSEEPROM = 121    # Read data from Seeprom plug-in
TABLEDATA =   122    # Write one byte of WAVETABLE to AVR EPROM

# Commands with Four bytes argument (151 to 180)
SETTIME =     161    # Set time. elaped seconds since 1970
PMRB_START =  162    # PMRB arg: number of 128 byte blocks, delay in seconds  

# Reply from Atmega16
DONE     =    'D'    # success
SUCCESS = ord('D')   # Byte representation of 'D'.
INVCMD =      'C'    # Invalid command
INVARG =      'A'    # Input data out of bounds
INVBUFSIZE =  'B'    # READBLOCK request exceeds buffer size
TIMEOUT    =  'T'    # Time interval measurement failed
NOCLOCK =     'N'    # Clock not set error, for PMRB
USBERROR =    'U'    # ATmega8 based USB interface reported error
ADCRNGERR =   'R'    # SPI ADC Range ERROR

TABLESIZE =   100    # number of points in the User defined waveform
USERWAVE =      2    # Wave form table from EEPROM, loaded by user
HRUSERWAVE =    3    # Wave Table from AVR EEPROM, to plug-in HRDAC

WIDTH =     300.0    # used by plot()
HALF_HEIGHT=100.0
YMAX     = 5000.0    #5000 mV


device_list = ['/dev/ttyS0','/dev/ttyS1','/dev/tts/USB0','/dev/tts/USB1',\
    '/dev/ttyUSB0','/dev/ttyUSB1',0,1,2,3]

logfile = None	     # To keep track of Hardware connection failures

def phm(dev = None):
    """
    Create an instance of the Class named 'Phm'. If the file descriptor to
    access the phoenix hardware in set, the instance is returned. Otherwise 
    None is returned.
    """
    global logfile
        
    logfile = open('phm.log','w')
    object = Phm()
    logfile.close()
    if object.handle != None:
        object.stop_wave()
        object.set_adc_size(object.adc_size)
        return object
    print 'Could not find Phoenix-M on RS232 or USB ports'
    print 'Check hardware connections.'

#----------------------- USB Version ----------------------------
VENDOR_ID    = 0x03eb    # Vendor ID of Atmel
PRODUCT_ID   = 0x21ff    # Atmega based usb interface
VDR          = 0xC0        # USB Vendor device request
RS_WRITE     = 10    
RS_READ      = 14
RS_SETBAUD   = 12

USBMAXTRY    = 500
BUFSIZE      = 1802            # status + adcinfo + 800 data

class Phm:
    buf = array.array('B',BUFSIZE * [0])    # unsigned character array, Global
    seeprom_active = 0    
    num_samples = 100       # 1 to 800
    current_chan = 0        # 0 to 3, used by get_voltage & read_block   
    num_chans = 1           # 1 to 4, used by multi_read_block
    chan_mask = 1           # First channel seleted
    adc_size = 1            # 1 or 2 bytes
    adc_delay = 10          # 10 to 1000 usecs, Atmega16 
    adc_format_bip = 0;     # 1 if through level shifter amplifier
    maxwaitds = 40          # timeout = 40 * 50 msec
    pulse_width = 13        # 1 to 1000 usecs
    pulse_pol = 0           # HIGH TRUE (0) or  LOW TRUE (1)
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

    def find_usb_phoenix(self):
        import usb
        global logfile
        logfile.write('Searching for USB version of Phoenix.\n')
        busses = usb.busses()
        for bus in busses:        
            devices = bus.devices
            for dev in devices:        # Search for AVRUSB
                if dev.idVendor == VENDOR_ID and dev.idProduct==PRODUCT_ID:
                    interface = dev.configurations[0].interfaces[0][0]
                    logfile.write('AVR309 found. Trying to Claim it..\n')
                    try:
                        self.handle = dev.open()
                        self.handle.setConfiguration(dev.configurations[0])
                        self.handle.claimInterface(interface)
                    except:
                        logfile.write('AVR309: Open/Claim Interface failed.\n')
                        logfile.write('Another program using it already ?.\n')
                        self.handle = None
                        return
                    self.usb_dev = True
                    logfile.write('Found USB Phoenix. Setting Baudrate..')
                    self.setbaud(38)
                    logfile.write('Clearing buffer\n')
                    self.clearbuf()
                    v = self.get_version()
                    if v == None:
                        logfile.write('No Phoenix on AVR309.\n')
                        self.handle = None
    
    def usb_reconnect(self):
        global logfile
        if self.usb_dev == False:
            print 'No active USB connection'
            return
        try:
            self.handle.releaseInterface()
        except:
            pass
        logfile = open('phm.log','w')
        logfile.write('Trying to Re-connect USB Link.\n')
        self.find_usb_phoenix()
        logfile.close()
                    
    def __init__(self, dev = None):
        """
        First searches for the USB version of Phoenix. If not found searches 
        on the RS232 ports and the USB-to-Serial adapters.
        Currently the software can support one USB device + one Serial device.
        Supporting multiple USB versions are not yet done.
        """
        global logfile
        logfile.write('Entering Phm..\n')
        try:
            self.find_usb_phoenix()
            self.last_message = 'Phoenix Hardware on USB'
            self.set_adc_size(self.adc_size)
        except:
            logfile.write('USB software support not working.\n')
            self.handle = None
            
        if self.handle != None:	   # Found a USB Phoenix
            return
            
        logfile.write('Searching for RS232 version of Phoenix.')
        # We did not find a USB phoenix. Now try serial one    
        self.handle = None
        for dev in device_list:
            logfile.write('Searching on %s\n'%dev)
            try:
                import serial
                self.handle = serial.Serial(dev, 38400, stopbits=1,\
                    timeout = 0.3, parity=serial.PARITY_EVEN)
                self.handle.flush()
                self.usb_dev = False
                v = self.get_version()
                if v[0] == 'p' and v[1] == 'h':    # we got it
                    logfile.write('Found version %s\n'%v)
                    self.handle.timeout = 3	   # larger timeout needed
                    self.last_message = 'Phoenix Hardware on' + str(dev)
                    return
                else:
                    logfile.write('No Phoenix on %s\n'%dev)
            except:
                logfile.write('Error Opening %s\n'%dev)
                self.handle = None     

#-------------------------Communication to Phoenix via ATmega8-USB-----------------          
    def write(self, val):
        if self.usb_dev == False:        # This is a RS232 device
            self.handle.write(chr(val))
        else:
            self.handle.controlMsg(VDR, RS_WRITE, 1, value = val)
            
    def setbaud(self, val):
        self.handle.controlMsg(VDR, RS_SETBAUD, 1, value = val, index = 0)
    
    def clearbuf(self):
        if self.usb_dev == False:   # Serial device
            self.handle.flush()
            return
        while 1:    
            part = self.handle.controlMsg(VDR, RS_READ, 800)
            if len(part) < 3:
                break

    def unpackPacket(self,bytesPerDataPacket, packet):
        # Needed to convert from signed longs to string.
        self.__unpack_format__ = 'B'*bytesPerDataPacket
        # Needed to convert from string to unsigned bytes.
        self.__pack_format__ = 'b'*bytesPerDataPacket
        # Convert data from signed to unsigned.
        data = struct.unpack(self.__unpack_format__, struct.pack(self.__pack_format__, *packet))
        return data
  
    def read(self, nb):     	# loop until getting 'nb' bytes
        if self.usb_dev == False: 	  # Read from RS232 device
            for index in range(nb):
                ch = self.handle.read()
                self.buf[index] = ord(ch)
            return index + 1
        # Read from USB device    
        index = 0	     
        remaining = nb
        timer = 0
        while remaining:
            if remaining <= 200:
                bsize = remaining
            else:
                bsize = 200
            part = self.handle.controlMsg(VDR, RS_READ, bsize + 2)
            if os.name != 'posix': # Workaround a PyUSB version problem.
                part = self.unpackPacket(len(part), part)
            if len(part) < 3:
                timer = timer + 1
                if timer > USBMAXTRY:
                    self.buf[0] = ord(USBERROR)
                    return 0
                continue;
            pl = len(part) - 2
            for k in range(2,len(part)):
                self.buf[index] = part[k]
                index = index + 1
            remaining = remaining - pl
        return index
    
    def last_msg(self):
        return self.last_message
        

# -------------------------- uC PORT I/O ---------------------------
    def set_ddr(self, port, direc):
        self.write(SETDDR)           
        self.write(port)	 # 0 to 3 for A,B,C and D
        self.write(direc)
        self.read(1)
        return

    def set_port(self, port, val):
        self.write(SETPORT)           
        self.write(port)	 # 0 to 3 for A,B,C and D
        self.write(val)
        self.read(1)
        return


    def get_port(self, port):
        self.write(SETPORT)           
        self.write(port)	 # 0 to 3 for A,B,C and D
        self.read(1)
        self.read(1)     	 # get the status byte only
        return self.buf[0]
        return

# -------------------------- Digital I/O ---------------------------
    def read_inputs(self):
        """
        Return a 4 bit number representing the voltage levels on the 
        four digital input sockets.
        Usage:
            p = phm()
            print p.read_inputs()
        """
        self.write(DIGIN)
        self.read(1)        # get the status byte only
        if self.buf[0] != SUCCESS:
            self.clearbuf()
            return None
        self.read(1)     	   # get the status byte only
        return self.buf[0] & 15

    def read_acomp(self):
        """
        Returns the status of Analog comparator
        1 if AN- is < 1.23V       
            p = phm()
            print p.read_acomp()
        """
        self.write(READACOMP)    # Error check ???
        self.read(1)
        if self.buf[0] != SUCCESS:
            return None
        self.read(1)
        return self.buf[0]

    def write_outputs(self, val):
        """
        Writes  a 4 bit number to the Digital Output Sockets
        Usage:
            p = phm()
            p.write_outputs(val)
        """
        self.write(DIGOUT)    # Error check ???
        self.write(val)
        self.read(1)
        return

    def pulse_out(self, data):
        """
        Send a Robosapien pulse on D3.
        """
        self.write(PULSEOUT)
        self.write(data)
        self.read(1)

#-------------------- Analog Outputs / Inputs ---------------------------

    def set_voltage(self, val):
        """
        Sets the PWM DAC between zero to 5000 mV
        Usage:
            s = phm()
            s.set_dac(val)
        """
        val = (val * 255.0) / 5000.0
        iv = int(val)
        
        self.write(SETDAC)
        self.write(iv)
        self.read(1)
        return

    def set_dac(self, val):
        """
        Sets the PWM DAC input raw value from 0 to 255
        Usage:
            s = phm()
            s.set_dac(val)
        """
        self.write(SETDAC)
        self.write(val)
        self.read(1)
        return

    def select_adc(self, val):
        """
        Selects the ADC channel to be digitized by the get_voltage() 
        and read_block() functions. Does not affect multi_read_block()
        Usage:
            s = phm()
            s.select_adc(val)
        """
        self.write(SETCURCHAN)
        self.write(val)
        self.read(1)
        self.current_chan = val
        self.set_adc_size(self.adc_size)  # set size also ???
        return

    def set_adc_size(self, val):
        """
        Sets the ADC datasize to 1 or 2 bytes. ATmega16 ADC is can
        be set to 10 bits or 8 bits resolution. For 10 bit resolution,
        the delay between digitizations should be set more than 100 
        microseconds.
        Usage:
            s = phm()
            s.set_adc_size(val)
        """
        self.write(SETADCSIZE)
        self.write(val)
        self.read(1)
        self.adc_size = val
        return

    def zero_to_5000(self):
        """
        Use get_voltage() instead of this function.
        """
        return self.get_voltage()

    def get_voltage(self):
        """
        Reads the voltage present at the Analog Input, selected using
        select_adc(0) function. Returns the system time stamp and the 
        voltage in millivolts,  0 to +5000 mV
        The return value is a tuple containing he PC timestamp and the
        voltage.
        """
        res = self.read_adc()
        if res == None:
            return None

        if self.adc_size == 1:
            volt = res[1] * 5000.0 / 255.0
        else:                # 10 bit data
            volt = res[1] * 5000.0 / 1023.0
        return (res[0],volt)

    def minus5000_to_5000(self):
        """
        Use get_voltage_bip() instead of this function.
        """
        return self.get_voltage_bip()

    def get_voltage_bip(self):
        """
        Analog Inputs take only 0 to 5V range signals. Bipolar signals
        are fed though the level shifting amplifiers. This function
        returns the voltage given at the input of the level shifter.
        Otherwise same as get_voltage().
        """
        res = self.read_adc()
        if res == None:
            return None

        if self.adc_size == 1:
            volt = res[1] * 10000.0 / 255.0 - 5000.0
        else:                # 10 bit data
            volt = res[1] * 10000.0 / 1023.0 - 5000.0
        return (res[0],-volt)

    def read_adc(self):
        """
        Digitizes the ADC input and returns the binary value.
        result is from 0 to 255 for adc_size = 1
        and 0 to 1023 if adc_size = 2.
        System time stamp also is returned to the caller
        The time stamp is used to find the time interval between
        two calls.
        """
        self.write(ADCREAD)
        self.read(1)
        if self.buf[0] != SUCCESS:
            return None
        t = time.time()   #add system time stamp
        if self.adc_size == 1:
            self.read(1)
            return (t, self.buf[0])
        else:
            self.read(2)
            val = (self.buf[1] << 8) | self.buf[0]
            return (t,val)
        
    def adc_input_period(self, ch):
        """
        Time between two rising edges on ADC Input. The signal must be a
        squarewave with more than 2 volts amplitude.
        """
        self.write(AINPERIOD)
        self.write(ch)
        self.read(1)
        if self.buf[0] != SUCCESS:
          return -1.0
        self.read(3)
        low = self.buf[1] << 8 | self.buf[0]
        return low + 50000 * self.buf[2]

    def read_block(self, np, delay, bip=0):
        """
        Returns a block of data from the ADC. The channel to be digitized
        is set by calling select_adc().
        The call returns a status byte, then another byte for adc_size
        followed by (np * adc_size) bytes of data. 
        For two byte ADC data, the lower byte of Dataword comes first
        Arguments:
            np : Number of points to digitize
            delay : Interval between samples in microseconds
            bip : 1 when using (x+5)/2 gain block, else 0
        """
        self.set_adc_delay(delay)        
        self.set_num_samples(np)
        self.write(READBLOCK)
        self.read(1)        # get Status
        if self.buf[0] != SUCCESS:
            self.clearbuf()
            return ['READBLOCK returned error %c'%self.buf[0]]
        self.read(1)        # get adcsize
        self.adc_size = self.buf[0]  >> 4
        nb = self.read(self.num_samples * self.adc_size)
        index = 0
        dat = []
        if self.adc_size == 1:
            for i in range(np):
                t = i * self.adc_delay
                if bip == 0:
                    volt = self.buf[index] * 5000.0 / 255
                else:
                    volt = self.buf[index] * 10000.0 / 255.0 - 5000.0
                    volt = -volt
                dat.append([t,volt])
                index = index + 1
        else:                # 10 bit data
            for i in range(np):
                t = i * self.adc_delay
                val = self.buf[index+1]
                val = (val << 8) | self.buf[index]
                if bip == 0:
                    volt = val * 5000.0 / 1023.0
                else:
                    volt = val * 10000.0 / 1023.0 - 5000.0
                    volt = -volt
                dat.append([t,volt])
                index = index + 2
        return dat


    def multi_read_block(self, np, delay, bip=0):
        """
        Returns a block of data from the ADC. 
        The channels to be digitized are set by add_channel() calls.
        The call returns a status byte, then another byte reporting
        a channel mask and adc_size.
        followed by (np * num_chans * adc_size) bytes of data. 
        For two byte ADC data, the lower byte of Dataword comes first
        Arguments:
            np : Number of points to digitize
            nchan : number of channels
            delay : Interval between samples in microseconds
            bip : 1 when using (x+5)/2 gain block, else 0
        With 10 usec conversion time only 1 channel selected the MULTIREADBLOCK call 
        is unable to meet timing requirements in the C code. 
        We treat it now as a special case
        """
        
        if self.num_chans == 1:   #Special case. 6-Aug-2010
           for ch in range(4):
               if self.chan_mask & (1<<ch):
                  self.select_adc(ch)
                  break
           buf = self.read_block(np,delay,bip) 
           self.select_adc(self.current_chan)   # restore the old value
           return buf
        
        self.set_num_samples(np)
        self.set_adc_delay(delay)        
        self.write(MULTIREADBLOCK)
        self.read(1)        # get status
        if self.buf[0] != SUCCESS:
            self.clearbuf()
            return ['MULTIREADBLOCK returned error %c'%self.buf[0]]

        self.read(1) 		    # get chmask
        chmask = self.buf[0]        #channel mask and ADC data size
        nc = 0
        for x in range(4):
          if (1 << x) & chmask:
            nc = nc + 1
        self.num_chans = nc    # Update nchan & size
        self.adc_size = chmask >> 4
        nb = self.num_samples * self.adc_size * nc
        if self.read(nb) != nb:
            return ['MULTIREADBLOCK returned error %c'%self.buf[0]]
        
        dat = []
        index = 0
        #print self.adc_delay
        if self.adc_size == 1:
            for i in range(np):
                item = []
                item.append(i * self.adc_delay*nc) # *nc added 8-Sep-07
                for chan in range(self.num_chans):
                    if bip == 0:
                        item.append(self.buf[index] * 5000.0 / 255)
                    else:
                        y = self.buf[index] * 10000.0 / 255.0 - 5000.0
                        item.append(-y)
                    index = index + 1
                dat.append(item)
        else:                # 10 bit data
            for i in range(np):
                item = []
                item.append(i * self.adc_delay*nc) # *nc added 8-Sep-07
                for chan in range(self.num_chans):
                    val = (self.buf[index+1] << 8) | self.buf[index]
                    if bip == 0:
                        item.append(val * 5000.0 / 1023.0)
                    else:
                        y = (val * 10000.0 / 1023.0 - 5000.0)
                        item.append(-y)
                    index = index + 2
                dat.append(item)
        return dat

    def add_channel(self, val):
        """Adds the channel to the MULTIREADBLOCK list    (0 to 3)
        Usage:
            s = phm()
            s.add_channel(val)
        """
        if val < 0 or val > 3: return
        self.write(ADDCHAN)
        self.write(val)
        self.read(1)
        if self.buf[0] != SUCCESS:
            return
        self.chan_mask |= (1 << val)
        self.num_chans = 0
        for k in range(4):
            if (1<<k) & self.chan_mask:
                self.num_chans += 1
        return
        
    def del_channel(self, val):
        """Deletes the channel from the MULTIREADBLOCK list (0 to 3)
        Usage:
            s = phm()
            s.del_channel(chan) 
        """
        if val < 0 or val > 3: return
        self.write(DELCHAN)
        self.write(val)
        self.read(1)
        if self.buf[0] != SUCCESS:
            return
        self.chan_mask &= ~(1 << val)
        self.num_chans = 0
        for k in range(4):
            if (1<<k) & self.chan_mask:
                self.num_chans += 1
        return
        
    def get_chanmask(self):
        """Returns the numbr of active channels used by MULTIREADBLOCK.
        and the adc_size. res = (adc_size << 4) | chanmask
        This is needed for programs calling MRB to interpret the data.
        Usage:
            s = phm()
            print s.get_numchans()
        """
        self.write(GETCHANMASK)
        self.read(1)
        if self.buf[0] != SUCCESS:
            return None
        self.read(1)
        self.chan_mask = self.buf[0] & 15
        return   self.chan_mask

    def set_adc_trig(self, tr1, tr2, shifted = 0):
        """
        Sets the ADC trigger Levels , Inital and final
        If tr1 < tr2 then +ive trigger
        """
        if shifted == 0:
            low = int (255.0 * tr1 / 5000.0)
            hi  = int (255.0 * tr2 / 5000.0)
        else:
            low = int (255.0 * (tr1 + 5000.0) / 10000.0)
            hi  = int (255.0 * (tr2 + 5000.0) / 10000.0)
        self.fd.write(chr(ADCTRIGLEVELS))
        self.fd.write(chr(low))
        self.fd.write(chr(hi))
        res = self.fd.read()

    def enable_rising_wait(self, pin):
        """
        Same as enable_wait_high()
        """
        return self.enable_wait_high(pin)

    def enable_wait_high(self, pin):
        """
        Defines the WAIT action for BLOCKREAD calls. Digitization
        starts after detecting a HIGH level on the specified Digital
        Input (0 to 3) or 4 (ACMP input)
        """
        if pin == 4:
            mask = 0
        else:
            mask = 1 << pin
            
        self.write(WAITACTION)
        self.write(1)
        self.write(mask)
        self.read(1)

    def enable_falling_wait(self, pin):
        """
        Same as enable_wait_low()
        """
        return self.enable_wait_low(pin)

    def enable_wait_low(self, pin):
        """
        Defines the WAIT action for Block Read calls. Digitization
        starts after detecting a Falling Edge on the specified Digital
        Input (0 to 3) or 4 (ACMP input)
        """
        if pin == 4:
            mask = 0
        else:
            mask = 1 << pin
            
        self.write(WAITACTION)
        self.write(2)
        self.write(mask)
        self.read(1)

    def disable_wait(self):
        """
        Clear all the WAIT type actions on Digital input sockets.
        """
        self.write(WAITACTION)
        self.write(0)
        self.write(0)
        self.read(1)

    def enable_set_high(self, pin):
        """
        Defines the SET action for Block Read calls. The specified
        Digital Output pin ia made HIGH  before starting digitization.
        """
        mask = 1 << pin
        self.write(SETACTION)
        self.write(1)        # 1 means SET BIT action
        self.write(mask)
        self.read(1)

    def enable_set_low(self, pin):
        """
        Defines the CLEAR action for BLOCKREAD calls. The specified
        Digital Output pin ia made LOW  before starting digitization.
        """
        mask = 1 << pin
        self.write(SETACTION)
        self.write(2)        # 2 means CLR BIT action
        self.write(mask)     # The bit to be cleared
        self.read(1)

    def enable_pulse_high(self, pin):
        """
        Defines the SET action for BLOCKREAD calls. A HIGH TRUE pulse
        is given to the Selected Digital Output before starting digitization.
        It is the responsibility of the caller to keep it HIGH
        before calling read_block()
        """
        mask = 1 << pin
        self.write(SETACTION)
        self.write(3)        # 3 means HIGH TRUE Pulse
        self.write(mask)
        self.read(1)

    def enable_pulse_low(self, pin):
        """
        Defines the SET action for BLOCKREAD calls. A LOW TRUE pulse
        is send on the Selected Digital Output before starting digitization.
        It is the responsibility of the caller to keep it HIGH
        before calling read_block()
        """
        mask = 1 << pin
        self.write(SETACTION)
        self.write(4)        # 4 means LOW TRUE Pulse
        self.write(mask)
        self.read(1)

    def disable_set(self):
        """
        Clear all the SET/CLR type actions on Digital outputs
        just before block_read() functions
        """
        self.write(SETACTION)
        self.write(0)        # 0 => No more  SET/CLR actions
        self.write(0)
        self.read(1)

    def set_num_samples(self, val):
        """Selects the number of samples per channel to be 
        digitized during the READBLOCK type calls
        num_samples * num_chans * adc_size <= BUFSIZE in bytes
        returns the new value on success or old value on failure.
        Usage:
            s = phm()
            ns = s.set_num_samples(val)
        """
        
        low = val & 255;
        hi = val >> 8;
        self.write(SETNUMSAMPLES)
        self.write(low)
        self.write(hi)
        self.read(1)
        if self.buf[0] == SUCCESS:
            self.num_samples = val    # failure keeps the old value
        return self.num_samples

    def set_adc_delay(self, val):
        """Sets the delay between conversions. 6 to 100 usecs
        for 8 MHz  clock. Delay below 100 usecs are not good for
        10 bit accuracy. 
        This function is internally used by Block read functions.
        """
        low = val & 255;
        hi = val >> 8;
        self.write(SETADCDELAY)
        self.write(low)
        self.write(hi)
        self.read(1)
        if self.buf[0] == SUCCESS:
            self.adc_delay = val
        return


#---------------- Wave Generation & counting -----------------------
    def set_frequency(self, freq):        # Freq in Hertz
        """
        Sets the output frequency of the square wave
        output on the Programmable Wave Generator pin of ATmega8.
        From 15Hz to 40000000 Hz (4 MHz) 
        It is not possible to set all values. The function
        sets the nearest possible value and returns it.
        Usage:
            p = phm()
            print s.frequency(1000)
        """
        if freq < 1:        # Disable PWG
            self.write(SETCOUNTER2)
            self.write(0)
            self.write(0)
            self.read(1)
            return 0

        div = [4000000.0, 500000.0, 125000.0, 62500.0, 31250.0,15625.0,3906.25]
        for i in range(7):
            clock_sel = i+1
            freq0 = div[i]
            if ( freq0/ freq) <= 256:
                break
        setpoint = freq0/freq
        if setpoint > 255:
            setpoint = 255
        OCR2 = int(setpoint)-1
#        print clock_sel, OCR2
        self.write(SETCOUNTER2)
        self.write(clock_sel)
        self.write(OCR2)
        self.read(1)
        if self.buf[0] != SUCCESS:
            return None
        if setpoint == 0:
            return freq0
        else:
            return freq0/(OCR2+1)

    def load_wavetable(self, v):
        """
        Sends the 250 bytes wavetable to the AVR internal EEPROM
        Returns number of bytes loaded, maximum is 250.
        """
        if len(v) > TABLESIZE:
            return 0;
        self.stop_wave()
#        print 'len = ', len(v)
        addr = 0
        for x in v:
            self.eeprom_write_byte(addr,x)
            addr = addr + 1        
        return addr-1

    def start_wave(self, freq, plugin = 0):
        """
        The wave form is generated on the DAC output by periodic output
        of data from a table. Table has to be stored in eeprom first.
        """
        
        for OCR0 in range(200):
            possible = 100.0/(OCR0+1)
            if freq >= possible:
                break;
        OCR0 = OCR0 +1
        self.write(SETWAVEFORM)
        self.write(OCR0)
        if plugin == 0:
            self.write(USERWAVE)
        else:
            self.write(HRUSERWAVE)
        self.read(1)
        fr = 1000000.0 / (100 * (OCR0+1)* 32)
        return fr

    def pulse_d0d1(self, freq):
        """
        The squae wave is generated on the D0 and D1
        by using TC0 ISR.
        """
        if freq < 0.1:
            self.stop_wave()
            return 0
        val = int(1000000.0/(64.0 * freq))
        if val > 65535:
            return 0
        low = val & 255;
        hi = val >> 8;
        self.write(PULSE_D0D1)
        self.write(low)
        self.write(hi)
        self.read(1)
        return  1.0/(64.0*val)

    def stop_wave(self):
        self.write(STOPWAVE)
        self.read(1)

    def measure_frequency(self):    # Returns freqency in Hertz
        """
        Measures the frequency of the 0 to 5V square wave
        at the counter input. Returns the value in Hertz.
        External input is given to the 16 bit counter TCNT1.
        The 8 bit counter runs in parallel with a 1 MHz clock.
        When TCNT0 reaches 100, it is cleared a another variable
        is incremented.
        Usage:
            s = phm()
            print s.get_frequency()
        """
        self.write(COUNT)
        self.read(1)
        if self.buf[0] != SUCCESS:
            return None
        self.read(3)
        tcnt0 = self.buf[0]
        low = self.buf[1]
        hi = self.buf[2]
        novflow = (hi << 8) | low
        count = novflow * 256.0 + tcnt0      # count in one second
        return count

#------------------------Time Interval Measurement routines-------------

    def __helper(self, cmd, pin1, pin2):    # pins 0 to 3
        """
        Used by time measurement functions below.
        Make an 8 bit mask from pin1 and pin2. Lower half is source pin
        for example pin1 = 0 , pin2 = 0, mask = 00010001
        """
        if pin1 == 4:        # First wait on Analog Comparator
            low = 0
        else:
            low = 1 << pin1    # digin pins
            
        if pin2 == 4:        # Second wait on Analog comparator
            hi = 0
        else:
            hi  = 1 << (pin2+4)
        mask = hi | low;
        self.write(cmd)
        self.write(mask)
        self.read(1)
        if self.buf[0] != SUCCESS:
            return -1.0
        self.read(3)
        low = (self.buf[1] << 8) | self.buf[0]
        return low + 50000 * self.buf[2]
    def r2ftime(self, pin1, pin2):
        """
        Arguments:
        Returns delay (in micro seconds) from a rising edge on
        pin1 to a falling edge on pin2
        The pins can be the same. (0 to 3)
        second pin = 4 means analog comparator input
        """
        return self.__helper(R2FTIME, pin1, pin2)

    def r2rtime(self, pin1, pin2):
        """
        Arguments:
        Returns delay (in micro seconds) from a rising edge on
        pin1 to a rising edge on pin2
        The pins must NOT be the same. (0 to 3)
        second pin = 4 means analog comparator input
        """
        return self.__helper(R2RTIME, pin1, pin2)

    def f2rtime(self, pin1, pin2):
        """Returns delay (in micro seconds) from a falling edge on
        pin1 to a rising edge on pin2
        The pins can be the same.
        second pin = 4 means analog comparator input
        """
        return self.__helper(F2RTIME, pin1, pin2)

    def f2ftime(self, pin1, pin2):
        """
        Arguments:
        Returns delay (in micro seconds) from a falling edge on
        pin1 to a falling edge on pin2
        The pins must NOT be the same. (0 to 3)
        second pin = 4 means analog comparator input
        """
        return self.__helper(F2FTIME, pin1, pin2)


    def multi_r2rtime(self, pin , skipcycles=0):
        """
        Time between two rising edges on the same input pin.
        separated by 'skipcycles' number of cycles.
        If skipcycles is zero the period of the waveform is returned.
        """
        if pin == 4:
            mask = 0
        else:
            mask = 1 << pin
        self.write(MULTIR2R)
        self.write(mask)
        self.write(skipcycles)

        self.read(1)
        if self.buf[0] != SUCCESS:
            return -1.0
        self.read(3)
        low = (self.buf[1] << 8) | self.buf[0]
        return low + 50000 * self.buf[2]

    def pendulum_period(self, pin):
        """
        Period of oscillation T from light barrier. 
        """
        if pin == 4:
            mask = 0
        else:
            mask = 1 << pin
        self.write(TPEND)
        self.write(mask)
        self.read(1)
        if self.buf[0] != SUCCESS:
            return -1.0
        self.read(3)
        low = (self.buf[1] << 8) | self.buf[0]
        return low + 50000 * self.buf[2]

    def set2rtime(self, pin1, pin2):
        """Returns delay (in micro seconds) from setting of
        pin1 to a rising edge on pin2
        The pins can be the same.
        second pin = 4 means analog comparator input
        """
        return self.__helper(SET2RTIME, pin1, pin2)

    def set2ftime(self, pin1, pin2):
        """Returns delay (in micro seconds) from setting of
        pin1 to a falling edge on pin2
        The pins can be the same.
        second pin = 4 means analog comparator input
        """
        return self.__helper(SET2FTIME, pin1, pin2)

    def clr2rtime(self, pin1, pin2):
        """Returns delay (in micro seconds) from clearing of
        pin1 to a rising edge on pin2
        The pins can be the same.
        second pin = 4 means analog comparator input
        """
        return self.__helper(CLR2RTIME, pin1, pin2)

    def clr2ftime(self, pin1, pin2):
        """Returns delay (in micro seconds) from clearing of
        pin1 to a falling edge on pin2
        The pins can be the same.
        second pin = 4 means analog comparator input
        """
        return self.__helper(CLR2FTIME, pin1, pin2)

    def pulse2rtime(self, tx, rx):
        """
        Arguments:
            tx : Pulse is send on this output pin (0 to 3)
            rx : Rising edge received on this pin , 0 to 4)
        """
        return self.__helper(PULSE2RTIME, tx,rx)

    def pulse2ftime(self, tx, rx):
        """
        Arguments:
            tx : Pulse is send on this output pin (0 to 3)
            rx : Rising edge received on this pin , 0 to 4
        """
        return self.__helper(PULSE2FTIME, tx,rx)

    def set_pulse_width(self, width):
        """
        Sets the 'pulse_width' parameter for pulse2rtime()
        and pulse100_out() calls
        """
        self.write(SETPULSEWIDTH)
        self.write(width)
        self.read(1)
        if self.buf[0] == SUCCESS:
            self.pulse_width = width

    def set_pulse_polarity(self, pol):
        """
        Sets the 'pulse_polarity' parameter for pulse2rtime()
        pol = 0 means HIGH TRUE pulse 
        """
        self.write(SETPULSEPOL)
        self.write(pol)
        self.read(1)
        if self.buf[0] == SUCCESS:
            self.pulse_pol = pol

#-------------- Routines for the Radiation detection plug-in module.-------------

    def start_hist(self):
        """
        Enables the Interrupt that handles the
        Pulse processing plug-in.
        """
        self.write(STARTHIST)
        self.read(1)

    def stop_hist(self):
        """
        Disables the Interrupt that handles the
        Pulse processing plug-in.
        """
        self.write(STOPHIST)
        self.read(1)

    def clear_hist(self):
        """
        Clear the Histogram memory at ATmega16
        """
        self.write(CLEARHIST)
        self.read(1)

    def read_hist(self):
        """
        Reads the Histogram memory to PC. 
        1 byte status + 1 byte header + 256 x 2 bytes of data
        Usage:
            s = phm()
            v = s.read_hist()
            s.plot(v)
        """

        self.write(READHIST)
        self.read(1)
        if self.buf[0] != SUCCESS:
            self.clearbuf()
            return None
        self.read(1)           # The pad byte
        nb = self.read(512)    # Histogram is 512 bytes
        if nb != 512:
            print 'HIST read data error'
            self.clearbuf()
            return None
        dat = []
        index = 0
        for i in range(256):
            val = self.buf[index+1]
            val = (val << 8) | self.buf[index]
            dat.append((i,val))
            index = index + 2
        return dat

# --------------------- Devices on the Front Panel Slot --------------------

    def init_LCD_display(self):
        """
        Enable and Clear the LCD display. Due to the plug-in modules
        LCD display is not initialized during powerup. This function
        MUST NOT be called if some other plug-in is connected.
        """
        self.write(LCD_INIT)
        self.read(1)

    def write_LCD(self, ch):
        """
        Write one character to LCD display
        """
        self.write(LCD_PUTCHAR)
        self.write(ord(ch))
        self.read(1)

    def message_LCD(self, msg):
        """
        Write one line ( <= 15 characters) to LCD display
        """
        self.init_LCD_display()
        n = 0
        for c in msg:
            self.write(WRITELCD)
            self.write(ord(c))
            self.read(1)
            n = n + 1
            if n == 16:
                break    

#----------------High Resolution ADC/DAC plug-in modules---------------
    hradc_initialized = False
    Vref = 2500.140		# reference in millivolts
    Rmask = 7
    RMAX  = 7			# maximum value of range is 7 (2.56V)
    hrchan = 0
    Gains = [128.0, 64.0, 32.0, 16.0, 8.0, 4.0, 2.0, 1.0]
    HRMAXCHAN = 15
    
    def hr_adc_init(self):
        """
        Must be called once to do the calibration etc.
        """
        self.write(HR_ADCINIT)
        self.read(1)
        if self.buf[0] != SUCCESS:
            print 'ADC Init failed: ', self.buf[0]
            return False
        self.hradc_initialized = True
        self.hr_select_adc(0)		# Select Channel 0 by default
        self.hrchan = 0
        return True
        
    def hr_select_adc(self, chan):
        """
        AD7718 SPI ADC select channel. Use the stored Range value.
        """
        if (chan > self.HRMAXCHAN) or (chan < 0): 
            print "Invalid Channel Error."
            return ['Channel from 0 to 11 only']
        if self.hradc_initialized == False: 
            self.hr_adc_init()        
        self.write(HR_SETCHAN)
        val = (int(chan) << 4) + self.Rmask
        self.write(val)
        self.read(1)
        self.hrchan = chan

    def hr_select_range(self, val):
        """
        AD7718 SPI ADC select Range. USe the current channel value.
        """
        if (val > self.RMAX) or (val < 0): 
            print "Invalid Range Error."
            return ['Invalid Range Specified']
        self.Rmask = val
        self.write(HR_SETCHAN)
        val = (int(self.hrchan) << 4) + self.Rmask
        self.write(val)
        self.read(1)

    def hr_internal_cal(self, chan):
        """
        AD7718 SPI ADC Calibrate the selcted channel
        """
        if (chan > self.HRMAXCHAN) or (chan < 0): 
            print "Invalid Channel Error."
            return
        self.write(HR_CALINT)
        self.write(chan)
        self.read(1)
        if self.buf[0] != SUCCESS:
            print 'HR_CALINT Error : ', self.buf[0]
            return ['HR_CALINT Error']
        self.read(3)
        offset = (self.buf[0] << 16) |(self.buf[1] << 8) | self.buf[2]
        self.read(3)
        gain = (self.buf[0] << 16) |(self.buf[1] << 8) | self.buf[2]
        return (offset, gain)


    def hr_external_cal(self, chan, zorfs):  # Zero or FS calib on chan
        """
        AD7718 SPI ADC Calibrate the selcted channel
        """
        if (chan > self.HRMAXCHAN) or (chan < 0): 
            print "Invalid Channel Error."
            return
        self.write(HR_CALEXT)
        if zorfs == 0:
            val = chan			# No MSB set for zero cal
        else:
            val = chan | 128		# MSB is set for FS cal
        self.write(val)
        self.read(1)
        if self.buf[0] != SUCCESS:
            print 'HR_CALEXT Error : ', self.buf[0]
            return ['HR_CALEXT Error']
        self.read(3)
        offset = (self.buf[0] << 16) |(self.buf[1] << 8) | self.buf[2]
        self.read(3)
        gain = (self.buf[0] << 16) |(self.buf[1] << 8) | self.buf[2]
        return (offset, gain)


    def hr_read_adc(self):
        """
        Digitizes the Addon ADC input and returns 1 status + 3 data bytes
        on success. Else timeout error.
        System time stamp also is returned to the caller
        The time stamp is used to find the time interval between
        two calls.
        """
        ADCERR = 8
        if self.hradc_initialized == False: self.hr_adc_init()        
        self.write(HRADCREAD)
        self.read(1)
        if self.buf[0] != SUCCESS:
            return ['TIMEOUT Error']
        self.read(4)		# order is : status, HIGH, MID & LOW
        status = self.buf[0]
        if (status & ADCERR) != 0:
            return ['ADC Range Error']
        val = (self.buf[1] << 16) |(self.buf[2] << 8) | self.buf[3]
        t = time.time()        #add system time stamp
        return (t,val)

    def hr_get_voltage(self):
        """
        Digitizes the SPI ADC and returns the output in millivolts
        """
        res = self.hr_read_adc()
        if len(res) == 1:		# Error return
            return res
        v = res[1] * 1.024 * self.Vref / (self.Gains[self.Rmask] * 2**24)
        return (res[0], v)

        
#----------------------------- SPI 16 bit DAC ------------------------
    def hr_set_dac(self, val):
        """Set the 16 bit DAC
        Usage:
            s = phm()
            s.hr_set_dac(65535)
        """
        low = val & 255;
        hi = val >> 8;
        self.write(HRSETDAC)
        self.write(low)
        self.write(hi)
        self.read(1)
        return

    def hr_set_voltage(self, val):
        """
        Sets the SPI DAC between 0 to 2.5V
        Usage:
            s = phm()
            s.hr_set_voltage(val)
        """
        val = (val * 65535.0) / self.Vref
        iv = int(val)
        self.hr_set_dac(iv)


# --------------------- SEEPROM Pluin ------------------------------

    def seeprom_read(self, addr, nbytes):
        """
        Usage:
            s = phm()
        """
        if nbytes > 255:
            return None
        self.spi_init()		# to go
        self.write(READSEEPROM)
        self.write( addr & 255)
        self.write( (addr>>8) & 255)
        self.write(nbytes & 255)
        self.read(1)
        if self.buf[0] != SUCCESS:
            print 'seeprom_read error'
            return None
        nb = self.read(nbytes)
        if nb != nbytes:
            print 'seeprom read got', nb
            return None
        v = []
        for k in range(nbytes):
            v.append(self.buf[k])     
        return v

    def copy_eep2seep(self, addr):
        """
        copy 128 bytes from EEPROM to SEEPROM, to the given 16 bit address
        """
        self.write(COPY_E2S)
        self.write(addr & 255)
        self.write(addr >> 8)
        self.read(1)
        if self.buf[0] != SUCCESS:
            print 'copy eep2seep error'

    def seeprom_verify(self, blocknum, data):
        """
        loads 128 bytes to EEPROM and then copies it to SEEPROM plugin, 
        begin at address = blocknum * 128
        """
        if len(data) != 128:
          print 'Data must be 128 bytes'
          return None
          
        for k in range(128):
            self.eeprom_write_byte(k, data[k])

        addr = blocknum * 128    
        self.spi_init()
        self.copy_eep2seep(addr)
        return self.seeprom_read(addr, 128)

    def pmrb_get_data(self):
        fb = self.seeprom_read(0,128);    # first block
        x = 0
        nblocks = (fb[x+1] << 8) | fb[x]
        delay   = (fb[x+3] << 8) | fb[2]
        npoints = (fb[x+5] << 8) | fb[4]
        size = fb[6]
        numchans = fb[7]
        chmask = fb[8]
        dummy = fb[9]
        start = (fb[x+13] << 24) |(fb[12] << 16) |(fb[x+11] << 8) |fb[10];

        lb = self.seeprom_read(nblocks*128, 4);    # TS from last block
        end = (lb[x+3] << 24) | (lb[2] << 16) |(lb[x+1] << 8) | lb[0];

        info = [npoints, delay, size, numchans, chmask, start, end]
        
        """        
        print info
        print npoints, delay, nblocks
        print size, numchans, chmask
        print time.ctime(start)
        print time.ctime(end)
        print 'Elapsed times(%6d, %d) ' %(end-start, npoints * delay)
        """
        
        raw = []    # get the Data here for formatting
        x = 14        # get remaining data from first block 
        while x < 128:
            raw.append(fb[x])
            x = x + 1
        block = 1    # read the remaining blocks
        while block < nblocks:
            v = self.seeprom_read(block*128, 128);
            block = block + 1
            for i in v:
              raw.append(i)

        # Now start formatting the data
        bip = 0
        dat = []
        x = 0
        for i in range(npoints):
            item = []
            item.append(i * delay)
            for chan in range(numchans):
                if size == 1:
                    item.append(raw[x])
                    x = x + 1
                else:
                    val = raw[x] | raw[x+1] << 8
                    item.append(val)
                    x = x + 2
            dat.append(item)
        return dat, info


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
        #from Tkinter import *
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
        now = int(time.time()+0.5)
        self.write(SETTIME)
        self.write(now & 255)
        self.write( (now>>8) & 255)
        self.write( (now>>16) & 255)
        self.write( (now>>24) & 255)
        self.read(1)
        return now
        
    def get_time(self):
        self.write(GETTIME)
        self.read(1)
        if self.buf[0] != SUCCESS:
            return None
        self.read(4)
        return (self.buf[3] << 24) | (self.buf[2] << 16) | \
                  (self.buf[1] << 8) | self.buf[0]


#----------------------SLOW Multi Read Block functions -------------------------
    def smrb_start(self, np, delay,bip):
        """
        Setup the TC0 interrupt to do periodic digitization of the 
        selected ADC channels.
        """
        self.set_num_samples(np)
        self.set_adc_delay(delay)        
        self.adc_format_bip = bip;
        self.write(SMRB_START)
        self.read(1)
        if self.buf[0] == SUCCESS:
            return 1
        else:
            return 0
        
    def smrb_status(self):
        """
        Returns True if smrb is still running
        """
        self.write(SMRB_STATUS)
        self.read(1)
        if self.buf[0] != SUCCESS:
            return None
        self.read(3)    		# get SMRB status
        nwords = self.buf[2] << 8 | self.buf[1]
        print 'SMRB stat ', self.buf[0], nwords
        return self.buf[0], nwords
        
    def smrb_getdata(self):
        """
        Returns the block of data collected by SMRB ISR
        This call returns the partial result. Call smrb_status() first
        to see whether the process is completed.
        """
        self.write(SMRB_GETDATA)
        self.read(1)
        if self.buf[0] != SUCCESS:
            return ['SMRB_GETDATA returned error %c'%self.buf[0]]

        self.read(3)		    #chmask + size + number of bytes coming
        chmask = self.buf[0]        #channel mask and ADC data size
        nc = 0
        for x in range(4):
          if (1 << x) & chmask:
            nc = nc + 1
        self.num_chans = nc    # Update nchan & size
        self.adc_size = chmask >> 4
        nb = self.buf[2] << 8 | self.buf[1]
        if self.read(nb) != nb:
            return ['SMRB_GETDATA returned error %c'%self.buf[0]]

        np = int(nb) / (nc * self.adc_size)
        print 'NP = %d NC = %d Size = %d'%(np,nc,self.adc_size)

        bip = self.adc_format_bip
        dat = []
        index = 0
        if self.adc_size == 1:
            for i in range(np):
                item = []
                item.append(i * self.adc_delay*nc) # *nc added 8-Sep-07
                for chan in range(self.num_chans):
                    if bip == 0:
                        item.append(self.buf[index] * 5000.0 / 255)
                    else:
                        y = self.buf[index] * 10000.0 / 255.0 - 5000.0
                        item.append(-y)
                    index = index + 1
                dat.append(item)
        else:                # 10 bit data
            for i in range(np):
                item = []
                item.append(i * self.adc_delay*nc) # *nc added 8-Sep-07
                for chan in range(self.num_chans):
                    val = (self.buf[index+1] << 8) | self.buf[index]
                    if bip == 0:
                        item.append(val * 5000.0 / 1023.0)
                    else:
                        y = (val * 10000.0 / 1023.0 - 5000.0)
                        item.append(-y)
                    index = index + 2
                dat.append(item)
        return dat


#----Serial EEPROM Plug-in based prom multi read block functions, PMRB----

    def pmrb_start(self, np, delay):
        self.spi_init()
        self.set_num_samples(np)
        self.set_adc_delay(delay)        
        chmask = self.get_chanmask()
        
        datasize = chmask >> 4;
        chmask = chmask & 15;
        nchan = 0
        for x in range(4):
          if (1 << x) & chmask:
            nchan = nchan + 1
        nbytes = 10 + np * datasize * nchan;    # Header + data
        nbytes = nbytes + 4 * (int(np/256) + 1) # one TS for 256 samples
        nblocks = int(nbytes/128) + 1
        """
        print 'NC CM ', nchan, chmask        
        print 'NB = ', nblocks, nbytes
        print 'Delay = ', delay
        """
        self.write(PMRB_START)
        self.write(nblocks & 255)
        self.write( (nblocks>>8) & 255)
        self.write(delay & 255)
        self.write( (delay>>8) & 255)
        self.read(1)
        if self.buf[0] == SUCCESS:
            return 1
        else:
            return 0

    def pmrb_running(self):
        """
        Returns True if PMRB is still running
        """
        self.write(PMRB_RUNNING)
        self.read(1)
        if self.buf[0] != SUCCESS:
            return None
        self.read(1)    # SMRB status
        return self.buf[0]

    def eeprom_write_byte(self,addr, dat):
        """
        Sends the one byte to the specified address of AVR internal EEPROM
        """
        self.write(TABLEDATA)
        self.write(addr)
        self.write(0)
        self.write(dat)
        self.read(1)
        if self.buf[0] != SUCCESS:
            print 'eeprom write byte error = ', self.buf[0], addr

    def get_mcustatus(self):
        self.fd.write(GETMCUSTAT)
        self.read(5)    # status + 4 bytes
        print 'res' ,self.buf[0]
        print 'DDRA = ', self.buf[1]
        print 'DDRB = ', self.buf[2]
        print 'DDRC = ', self.buf[3]
        print 'DDRD = ', self.buf[4]

    def get_version(self):
        self.write(GETVERSION)
        nb = self.read(6)
        if self.buf[0] != SUCCESS:
            return 
        v = ''
        for x in range(1,6):
            v = v + chr(self.buf[x])
        return v

#------------------- Fine control of Software SPI -----------------
    """
    There are two kinds on SPI devices, it looks like. Some of them
    require the CLOCK to be LOW when CS goes LOW. Other type require CLOCK
    to be HIGH when CS is taken LOW. We need different routines to handle them.
    """
    def chip_enable(self, dev):
        self.write(CHIP_ENABLE)
        self.write(dev & 255)
        self.read(1)
        if self.buf[0] != SUCCESS:
            print 'Chip Enable Error'

    def chip_enable_bar(self, dev):
        self.write(CHIP_ENABLE_BAR)
        self.write(dev & 255)
        self.read(1)
        if self.buf[0] != SUCCESS:
            print 'Chip Enable_bar Error'

    def spi_push(self, dat):
        self.write(SPI_PUSH)
        self.write(dat & 255)
        self.read(1)
        if self.buf[0] != SUCCESS:
            print 'SPI Push Error', chr(self.buf[0])

    def spi_push_bar(self, dat):
        self.write(SPI_PUSH_BAR)
        self.write(dat & 255)
        self.read(1)
        if self.buf[0] != SUCCESS:
            print 'SPI Push Error', chr(self.buf[0])

    def spi_pull(self):
        self.write(SPI_PULL)
        res = self.read(1)
        if self.buf[0] != SUCCESS:
            print 'SPI Pull Error'
            return None
        self.read(1)
        return self.buf[0]

    def spi_pull_bar(self):
        self.write(SPI_PULL_BAR)
        res = self.read(1)
        if self.buf[0] != SUCCESS:
            print 'SPI Pullbar Error'
            return None
        self.read(1)
        print self.buf[0]
        return self.buf[0]

    def chip_disable(self):
        self.write(CHIP_DISABLE)
        self.read(1)
        if self.buf[0] != SUCCESS:
            print 'Chip Disable Error'

#---------------------------- GM Tube routines ---------------------
    gmcal = [ \
( 280, 5), ( 268, 6), ( 292, 7), ( 319, 8), ( 343, 9), ( 370, 10),\
( 386, 11), ( 406, 12), ( 418, 13), ( 430, 14), ( 445, 15), ( 457, 16),\
( 469, 17), ( 477, 18), ( 485, 19), ( 493, 20), ( 501, 21), ( 504, 22),\
( 508, 23), ( 504, 24), ( 504, 25), ( 508, 26), ( 504, 27), ( 504, 28),\
( 504, 29), ( 504, 30), ( 504, 31), ( 504, 32), ( 504, 33), ( 501, 34),\
( 508, 35), ( 508, 36), ( 512, 37), ( 516, 38), ( 520, 39), ( 524, 40),\
( 532, 41), ( 532, 42), ( 536, 43), ( 544, 44), ( 548, 45), ( 556, 46),\
( 564, 47), ( 564, 48), ( 568, 49), ( 575, 50), ( 575, 51), ( 583, 52),\
( 591, 53), ( 595, 54), ( 599, 55), ( 603, 56), ( 611, 57), ( 615, 58),\
( 615, 59), ( 619, 60), ( 619, 61), ( 627, 62), ( 627, 63), ( 623, 64),\
( 623, 65), ( 623, 66), ( 627, 67), ( 627, 68), ( 627, 69), ( 631, 70),\
( 638, 71), ( 638, 72), ( 638, 73), ( 642, 74), ( 646, 75), ( 650, 76),\
( 658, 77), ( 658, 78), ( 658, 79), ( 666, 80), ( 670, 81), ( 678, 82),\
( 682, 83), ( 686, 84), ( 690, 85), ( 698, 86), ( 705, 87), ( 713, 88),\
( 717, 89), ( 729, 90), ( 737, 91), ( 737, 92), ( 749, 93), ( 757, 94),\
( 765, 95), ( 769, 96), ( 772, 97), ( 780, 98), ( 784, 99), ( 792, 100),\
( 800, 101), ( 804, 102), ( 808, 103), ( 824, 104), ( 820, 105), ( 824, 106),\
( 828, 107), ( 832, 108), ( 839, 109), ( 839, 110), ( 847, 111), ( 843, 112),\
( 855, 113), ( 859, 114), ( 859, 115), ( 871, 116), ( 875, 117), ( 887, 118),\
( 887, 119), ( 895, 120), ( 903, 121), ( 910, 122), ( 918, 123), ( 922, 124),\
( 930, 125), ( 938, 126)]
    gmtv_scale = (2 * 5.6 + 0.056)/0.056/1000. # V divider 56K and 11.2M

    def gm_get_count(self, dur=1):
        count = 0
        for k in range(dur):
            count = count + self.measure_frequency()
        return count
        
    def gm_get_voltage(self):
        self.select_adc(0)
        self.set_adc_size(2)
        v = self.get_voltage()[1] * self.gmtv_scale
        return v
        
    def gm_set_voltage(self,tv):
        MAXTRY = 15
        dac = 0
        for m in range(len(self.gmcal)):
            if  self.gmcal[m][0] > tv:
                dac = int(self.gmcal[m][1])
                break
        for k in range(MAXTRY):
            self.set_dac(dac)
            time.sleep(0.2)
            v = self.gm_get_voltage()
#            print 'GM ',tv,v
            if abs(tv-v) < 5:
                break
            if v < tv and dac < 126:
                dac = dac + 1
            elif v > tv and dac > 1:
                dac = dac - 1
        return v

