# Accleration due to gravity using a Rod pendulum 
import phm, math
p=phm.phm()

length = 7.0			# length of the rod pendulum
pisqr = math.pi * math.pi

for i in range(50):
  T = p.pendulum_period(3)/1000000.0
  g = 4.0 * pisqr * 2.0 * length / (3.0 *  T * T)
  print i, ' ',T, ' ', g

