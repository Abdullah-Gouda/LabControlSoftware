import time 
import datetime
import operator

class myTime:
	def __init__(self,stringtime="00:00"):
		temp = stringtime.split(":")
		self.hours = int(temp[0])
		self.minutes = int(temp[1])
	


# get hours and minutes from minutes  as string
def gethoursandminutes(processingTime): 	 
	hours = processingTime / 60 
	minutes = processingTime % 60
	temptime =str(hours) + ":"+str(minutes)
	return temptime

def getlocaltime(): # in hours and minutes as a string
	#getting current local time
	localtime = time.ctime()
	print localtime        # Fri Jan  1 01:59:20 2016
	return localtime[11:16]

def getendtimestr(endtime): # endtime = "1400"
	temp = len(endtime)
	#print "length: ",temp
	if temp == 3:	
		hours = endtime[0]
		minutes = endtime[1:2]

	elif temp == 4:
		hours = endtime[0:2]
		minutes = endtime[2:4]
		
	temptime =str(hours) + ":"+str(minutes)
	return temptime

def addtimes(time1,time2,time3):
	tempminutes = time1.minutes + time2.minutes 
	time3.hours = time1.hours + time2.hours + tempminutes/60
	time3.minutes = tempminutes % 60
	return time3
	


def main():
	contractList = {}
	contractList['shuttle3'] = {'contNum':3,"periority":3,"EndTime":14,"processingTime":30}
	print contractList


	tasks = {'task1':3,'tsk2':1,'task3':2}
	sortdtasks = sorted(tasks.items(),key=operator.itemgetter(1))
	print "sorted tasks ",sortdtasks

	now = datetime.datetime.now()
	print "now ",now
	aa = now.replace(hour = 2 ,minute = 0 ,second = 0 ,microsecond = 0)
	print aa
 	#task1
	# processing time  
	processingtimestr = gethoursandminutes(30)
	print processingtimestr
	processingtime = myTime(processingtimestr)
	print "processingtime time -->> ", processingtime.hours,":",processingtime.minutes


	#current time
	localtime = getlocaltime()
	print "local test :",localtime
 	currenttime = myTime(localtime)
	print "current time -->> ", currenttime.hours,":",currenttime.minutes



	test = getendtimestr("1600")
 	print test
	#End time 
	endtime = myTime(test)
	print "endtime time -->> ", endtime.hours,":",endtime.minutes
	wt1 =  myTime()
	addtimes(processingtime,currenttime,wt1)
	print "worst case end time ", wt1.hours,":",wt1.minutes


 	#task2
	# processing time  
	task2processingtimestr = gethoursandminutes(15)
	print task2processingtimestr
	task2processingtime = myTime(task2processingtimestr)
	print "task2 processingtime time -->> ", task2processingtime.hours,":",task2processingtime.minutes


	#current time
	localtime = getlocaltime()
	print "local test :",localtime
 	currenttime = myTime(localtime)
	print "current time -->> ", currenttime.hours,":",currenttime.minutes



	task2test = getendtimestr("1530")
 	print task2test
	#End time 
	task2endtime = myTime(task2test)
	print "task2 endtime time -->> ", task2endtime.hours,":",task2endtime.minutes
	task2wt1 =  myTime()
	addtimes(task2processingtime,wt1,task2wt1)
	print "task2 worst case end time ", task2wt1.hours,":",task2wt1.minutes

	

if __name__ == "__main__":
	main()
