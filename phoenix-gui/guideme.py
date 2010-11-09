'''
   guideme.py - Program for doing several experiments using Phoenix
   Copyright (C) 2008 Ajith Kumar, Inter-University Accelerator Centre,
   New Delhi. 

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3, or (at your option)
   any later version.

   Last edited on 30-Jun-2009 : Added the re-connect option to handle
   temporary loss of USB connection, due to any contact/power problem.
   Added an Offline mode , just to browse the menus.
'''

from Tkinter import *
import Image, ImageTk, os
import phm

import disp, textwin, utils
import primer, capacitor, induction, pendulum, transformer, diode, gravity
import osc555, mono555, radiation, pt100, usound, rodpend, gm

photo_sizes = [(300,233), (350, 272), (451,350)]
def getsize(w):
    x,y = w.wm_maxsize()
    if x < 700:			# 640 x 480 screen
        return photo_sizes[0]
    elif x < 1000:		# 800 x 600 screen
        return photo_sizes[1]
    else:			# 1024 x 768 or more
        return photo_sizes[2]

def timer():			# Timer loop
    global fd, offline
    try:
        active_expt.update()
    except:
        if offline != True:
            msgwin.msg('Error. Trying re-connect','red')
    root.after(10, timer)

def quit():
  sys.exit()

def reconnect():
    global fd
    fd.usb_reconnect()
    if fd == None:
       s = 'Connection to Phoenix Hardware Failed. Try again.\n'
       msgwin.msg(s, 'red')
       return
    msgwin.msg('Found Phoenix Hardware ' + fd.last_msg(), 'black')
    root.title(fd.last_msg())

def connect():
    global fd, offline
    if offline == False:    # Already Online
        msgwin.msg('Already Connected. ' + fd.last_msg(), 'black')
        return
    fd = phm.phm()	    # Create Phm Object, find Hardware
    if fd == None:
        import offline
        fd = offline.phm()
        offline = True
        root.title('No Hardware Connection, running offline')
        msgwin.msg('No Hardware Connection, running offline', 'red')
        return
    msgwin.msg('Found Phoenix Hardware ' + fd.last_msg(), 'black')
    root.title(fd.last_msg())
    offline = False
    if active_expt != None:
        switch_expt(active_expt)

#----------------------------------------------------------------------
def help():
    try: 
        fname = utils.help_file_abspath(active_expt.file) 
        os.system ('firefox file://' + fname + '&')
    except:
        msgwin.msg('No help file available for '+ active_expt.label)

def switch_expt(expt):
    global active_expt, fd
    if active_expt != None:
        active_expt.exit()
        active_expt.canvas.pack_forget()	# Remove Current Expt
    expt.canvas.pack()
    plot2d.delete_lines()
    active_expt = expt
    msgwin.msg('Selected Experiment is '+ expt.label)
    expt.enter(fd)
#--------------------------------------------------------------------          
offline = True			# Assume Offline
physics = []
electronics = []
active_expt = None		# Curently active experiment
fd = None			# Phoenix hardware handler

root = Tk()		
size = getsize(root)
f = Frame(root)			# make the widgets
f.pack(side=TOP)
left = Frame(f, bg = 'white')
left.pack(side = LEFT, anchor = NW)
right = Frame(f, bg= 'white')
right.pack(side = LEFT, fill = X, expand = 1)

# Create the plot2d window & message window Objects
plot2d = disp.disp(right, size[0], size[1],'ivory')
msgwin = textwin.textwin(root, 50, 15)

#Create Expt objects. Pass canvas size, plot2d and msgwin objects
Primer = primer.explore(left, size, plot2d, msgwin)
Primer.label = 'Explore Phoenix'

#List of Physics Experiments
Cap = capacitor.cap(left, size, plot2d, msgwin)
Cap.label = 'Capacitor Charging'
Cap.file = 'capacitor.html'
physics.append(Cap)
Induction = induction.induction(left, size, plot2d, msgwin)
Induction.label = 'Electromagnetic Induction'
physics.append(Induction)
Trans = transformer.tran(left, size, plot2d, msgwin)
Trans.label = 'Mutual Induction between coils'
physics.append(Trans)
Pendulum = pendulum.pend(left, size, plot2d, msgwin)
Pendulum.label ='Pendulum Waveform'
physics.append(Pendulum)
Rodpend = rodpend.rodpend(left, size, plot2d, msgwin)
Rodpend.label = 'Rod Pendulum measuring gravity'
physics.append(Rodpend)
Gravity = gravity.gravity(left, size, plot2d, msgwin)
Gravity.label = 'Gravity by Time of Flight'
physics.append(Gravity)
Sound = usound.sound(left, size, plot2d, msgwin)
Sound.label = 'Study Sound with 40KHz Piezo '
physics.append(Sound)
Pt100 = pt100.pt100(left, size, plot2d, msgwin)
Pt100.label = 'Temperature (PT100)'
physics.append(Pt100)
Rad = radiation.rad(left, size, plot2d, msgwin)
Rad.label = 'Radiation Detection (MCA)'
physics.append(Rad)
Gm = gm.gm(left, size, plot2d, msgwin)
Gm.label = 'GM Counter'
physics.append(Gm)

#List of Electronics Experiments
Diode = diode.diode(left, size, plot2d, msgwin)
Diode.label = 'Diode Characteristic'
electronics.append(Diode)
Osc555 = osc555.osc(left, size, plot2d, msgwin)
Osc555.label = 'Oscillator (555)'
electronics.append(Osc555)
Mono555 = mono555.mono(left, size, plot2d, msgwin)
Mono555.label = 'Mono Shot (555)'
electronics.append(Mono555)

#Add the Menus
menubar = Menu(root)
first = Menu(menubar, tearoff=0)
first.add_radiobutton(label='USBReConnect', command = reconnect)
first.add_radiobutton(label='Connect Hardware', command = connect)
menubar.add_cascade(label="Connection", menu=first)

phy = Menu(menubar, tearoff=0)
for expt in physics:
    phy.add_radiobutton(label=expt.label, command = lambda \
        expt=expt :switch_expt(expt))
menubar.add_cascade(label="Physics", menu=phy)

elec = Menu(menubar, tearoff=0)
for expt in electronics:
    elec.add_radiobutton(label=expt.label, command = lambda \
        expt=expt :switch_expt(expt))
menubar.add_cascade(label="Electronics", menu=elec)

menubar.add_command(label="Explore", command = lambda pr=Primer : \
        switch_expt(Primer))

menubar.add_command(label="Help", command = help)

root.config(menu=menubar)
connect()
switch_expt(Primer)
root.after(100, timer)
root.mainloop()
