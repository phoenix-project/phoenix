from phm import *
from pygame import *

sa= 261.63
re= 279
RE= 294
ga= 313
GA= 327
MA= 348
ma= 370
PA= 392
DHA= 436
dha= 418
NI= 490
ni= 470
SA= 523

init()
display.set_mode([100,100])
p=phm()
c='s'
x=0
while 1:
	k=event.wait()
	c
	try:
	 c= k.unicode
	except:
         c='0'
  
	if(c=='z'):
	   x=sa
	elif(c=='x'):
	   x=RE   
	elif(c=='c'):
	   x=GA   
	elif(c=='v'):
	   x=MA   
	elif(c=='b'):
	   x=PA   
	elif(c=='n'):
	   x=DHA  
	elif(c=='m'):
	   x=NI   
	elif(c==','):
	   x=SA   
	elif(c==' '):
	   exit(1)   
	else :
	   c=0
	p.set_frequency(x)
	time.delay(100)
	p.set_frequency(0)   
	   
