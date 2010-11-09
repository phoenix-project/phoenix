import os, sys

def abs_path(imagefile):
        name = sys.argv[0]
        dirname = os.path.dirname(name)
        if dirname != '':
            name = os.path.dirname(name) + os.sep + 'pics' + os.sep + imagefile
        else:
            name = 'pics' + os.sep + imagefile
        return name

def help_file_abspath(fname):
        path = os.path.abspath(sys.argv[0])
        hf = path.replace('guideme.py','html'+os.sep + fname)
        return hf

class Data:
    colors = ['black', 'red', 'green', 'blue', 'yellow','magenta','cyan']
    index = 0
    points = []
    traces = []
    xlabel = 'x'
    ylabel = 'y'

    def __init__(self):
        pass
        
    def clear(self):
        self.index = 0
        self.points = []
        self.traces = []

    def save(self, fname):
        f = open(fname,'w')
        for pt in self.points:
          s = '%7.5f %5.3f\n'%(pt[0], pt[1])
          f.write(s)
        f.close()  

    def save_all(self, fname):
        f = open(fname,'w')
        for tr in self.traces:
          for pt in tr:
            s = '%6.5f %4.3f\n'%(pt[0], pt[1])
            f.write(s)
          f.write('\n')
        f.close()  

    def analyze(self, xlabel, ylabel):	# Send Last Trace to Xmgrace
      try:
        import pygrace
      except:
        return
      if self.points != []:
        x = []
        y = []
        for k in self.points:
          x.append(k[0])
          y.append(k[1])
        pg = pygrace.grace()
        pg.plot(x,y)
        pg.xlabel(xlabel)
        pg.ylabel(ylabel)

    def get_col(self):
        if self.index < len(self.colors):
          col = self.colors[self.index]
        else:
          c = self.index * 10
          col = '#%2x%2x%2x'%(c,c,c)
        self.index = self.index + 1
        return col

