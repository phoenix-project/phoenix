from Tkinter import *
import Image, ImageTk, operator, sys

fp = open('coord.dat','w')

def quit():
  sys.exit()
  
def action(e):
  s = '%d %d\n'%(e.x,e.y)
  fp.write(s)
  print e.x/1000., e.y/781.0

root = Tk()
im = Image.open('pics/panel.jpg')
f = Frame(root)
f.pack()
image = ImageTk.PhotoImage(im)
c = Canvas(f, width = im.size[0], height = im.size[1])
c.create_image(0,0,image = image, anchor = NW)
c.bind("<ButtonRelease-1>", action)
c.bind("<Motion>", action)
c.pack()

b = Canvas()

#x = c.create_window(10, 10, window = b, anchor = NW)
c.pack()
b = Button(text = 'quit', command = quit)
b.pack()
root.mainloop()
