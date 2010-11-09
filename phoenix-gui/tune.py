#Author : Jithin B.P., jithinbp@gmail.com
#Distributed under GNU General Public License

sa2=261.63
re2=277.03
RE2=294.35
ga2=314.02
GA2=328.49
ma2=348.83
MA2=369.36
pa2=392.46
dha2=415.55
DHA2=441.54
ni2=233.08
NI2=246.94

sa=261.63
re=277.03
RE=294.35
ga=314.02
GA=328.49
ma=348.83
MA=369.36
pa=392.46
dha=415.55
DHA=441.54
ni=471.04
NI=492.75
SA=523.26

happy=[sa,sa,RE,2,sa,2,ma,2,GA,4,0,2,sa,sa,RE,2,sa,2,pa,2,ma,4,0,2,sa,sa,SA,2,DHA,2,
ma,2,GA,2,RE,4,0,2,ni,ni,DHA,2,ma,2,pa,2,ma,4]

import phm, time
p=phm.phm()
for a in happy:
	if(a < 11):	# it is a delay
	  time.sleep(float(a)/10)
	else :
	  p.set_frequency(a*2);
	  time.sleep(0.25)
p.set_frequency(0)
