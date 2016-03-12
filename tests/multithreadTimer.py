from threading import Timer,Thread

import time
import operator


class myTimer(Thread):
	def	__init__(self,minutes):
			Thread.__init__(self)
			print "thread init started.."
			self.delayTime = minutes 
			self.remainingTime = minutes

	def run(self):
		print "thread run started.."
		while self.remainingTime :
			self.decreaseTime()

			
	def decreaseTime(self):
		print "thread decreaseTime started.."
		self.remainingTime-=1
		time.sleep(60)

	def getRemainingTime(self):
		return self.remainingTime	

		

''' timer to notify after the desired time 
input : 1- amout of time in minutes
	 2- handler to be executed after timeout 
''' 
class tracingTimer():
	def	__init__(self,minutes,timeoutHandler):
			t=Timer(minutes * 60,timeoutHandler) 
			t.start()
			print ("Timer for %d minutes started "% minutes)

shutdown = False

def timeout():
	print "game over"
	global shutdown
	shutwon = True



def main():

	#t=Timer(1*60,timeout) 
	#t.start()
	#t1 = myTimer(1)
	#t1.run()
	mydic = {'shuttle_1':3,'shuttle_2':10,'shuttle_3':2}
	print "max: ",max(mydic.iteritems(),key=operator.itemgetter(1))[0]
	t2 =tracingTimer(1,timeout)

if __name__ == "__main__":
	main()
