from Tkinter import *
import tkFont


class textwin:
    win = None
    
    def select_font(self):	# Need to work on this
      return 'helvetica'
    
    def __init__(self, parent, width=400., height=300.,color='white'):
	self.parent = parent
	self.font = tkFont.Font(family = self.select_font(), size = 12)
	self.scrollbar = Scrollbar(parent)
	self.scrollbar.pack(side=RIGHT, fill=Y)
	f = Frame(self.parent)
	f.pack(side = TOP, fill = BOTH, expand = 1)
	self.win = Text(f, width = width, height = height,\
           font = self.font, fg = 'black', bg = color, spacing2 = 10,\
           wrap=WORD, yscrollcommand=self.scrollbar.set)
	self.win.pack(side = TOP, fill = BOTH, expand = 1)
	self.scrollbar.config(command=self.win.yview)
	self.label = Label(f, bg = 'white')
	self.label.pack(side = TOP, fill = X)
	self.tags = []
        self.tag_int = 0

    def gen_tag(self):
        self.tag_int = self.tag_int + 1
        t = str(self.tag_int)
        self.tags.append(t)
        return t

    def show_hand_cursor(self,w):
        self.win.config(cursor = 'hand2')
        
    def show_xterm_cursor(self,w):
        self.win.config(cursor = 'xterm')

    def showtext(self, msg, fg = 'black', bg = 'white'):
        t = self.gen_tag()
        self.win.tag_config(t, foreground = fg, background = bg,\
        spacing1 = 7, spacing2 = 7, justify = LEFT)
        self.win.insert(END, msg, (t))

    def showlink(self, msg, func):
        t1 = self.gen_tag()
        self.win.tag_config(t1, foreground = 'blue', underline = 1,\
        spacing1 = 7, spacing2 = 7,  justify = LEFT)
        t2 = self.gen_tag()
        self.win.tag_bind(t2, "<Button-1>", func)
        self.win.tag_bind(t2, "<Enter>", self.show_hand_cursor)
        self.win.tag_bind(t2, "<Leave>", self.show_xterm_cursor)
        self.win.insert(END, msg, (t1,t2))

    def showwindow(self, win):
        self.win.window_create(INSERT, window = win, padx = 1, align=BOTTOM)
        self.win.pack()
        
    def clear(self):
        self.win.delete(1.0, END)  

    def msg(self,s, col = 'black'):            
        self.label.config(text = s, fg = col)
        