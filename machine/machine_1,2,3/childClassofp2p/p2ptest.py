import machine_queue
from machine_queue import queueElement
import timeTest
from timeTest import myTime

import datetime
import operator
import sys  
import signal 
import os
from subprocess import call

sys.path.append('/home/bedo/github/MasterWork/common')
from p2p_framework import P2P_Interface
from testClass import myClass

 



class Machine(P2P_Interface):


	def __init__(self,shutdown, name, type, router_address,trnsportTime):
		P2P_Interface.__init__(self,shutdown, name, type, router_address)
		print "child koko ....."
		self.__newTaskArrived = False 
		self.__scheduleFail = False
		self.__newTask = {}
		self.__taskDic={}
		self.__transportationTime = trnsportTime
		signal.signal(signal.SIGINT,self.kill_signal_handler)
		print "pid is : ",os.getpid()
	
	def kill_signal_handler(self,signal,frame):
		print "you pressed ctrl+c !!"
		self.shutdown[0]
		call(["kill","-9",str(os.getpid())])
		



	def __del__(self):
		print "machine destructor......"
	
	def print_elements_queue(self):
		print "|\tTask name\t|\tStart Time\t|\tFinish Time\t|\tProcessing Time\t|\tDeadline\t|\tStatus"
		print "|\t---------\t|\t----------\t|\t-----------\t|\t---------\t|\t------\t\t|\t-------"
		for key,value in self.__taskDic.iteritems():
			print("|\t%s\t|\t%d:%d\t\t|\t%d:%d\t\t|\t%d:%d\t\t|\t%d:%d\t\t|\t%s\t\t"%(key,value._StartTime/3600,(value._StartTime%3600)/60,value._WorstCaseFinishingTime/3600,(value._WorstCaseFinishingTime%3600)/60,value._ProcessingRmainingTime/3600,(value._ProcessingRmainingTime%3600)/60,value._EndTime/3600,(value._EndTime%3600)/60,value._Status))


	# create new task object and add it to the the task queue of the machine
	def addNewTask(self,task):
		tempdic = {}
		key = task.keys()
		print key[0]
		tempdic[key[0]] = task[key[0]]
		self.__taskDic[key[0]] = queueElement(tempdic[key[0]]['priority'],tempdic[key[0]]['endTime'],tempdic[key[0]]['processingTime'],key[0])
		print "task added to self.__dic :",self.__taskDic
		self.__newTaskArrived = True
		task.clear()
		tempdic.clear()
		self.scheduleTasks(self.__taskDic)
 
####################################################33
	def converttoseconds(self,strtime):

		temp =timeTest.getendtimestr(strtime)
		#print temp 
		temp = myTime(temp)
		seconds = (temp.hours * 60 + temp.minutes) * 60
		return seconds


######################################################
	def getCurrentTimeInSeconds(self):
		currenttime = datetime.datetime.now()
		currenttimeinseconds = ( currenttime.hour * 60 + currenttime.minute ) * 60
		return currenttimeinseconds

##############################################
	def scheduleTasks(self,tasksDic):
			tasksEndTime ={}
			currenttimeinseconds = self.getCurrentTimeInSeconds()
			# stop running task and calculate remainng time  
			for key,value in tasksDic.iteritems():
				if value._Status == 'Running':
					value._Status = 'Stopped'
					value._ProcessingRmainingTime =value._WorstCaseFinishingTime - currenttimeinseconds  
				
					print ("Running task %s started at %f , remaining time : %f  stopped..."% (value._Name,value._StartTime/3600.0,value._ProcessingRmainingTime/3600.0))
				
				

			for key,value in tasksDic.iteritems():
				tasksEndTime[key] =value._EndTime 
			#print "unsorted task Queue of the machine :",tasksEndTime
			# sort the tasks according to their endtime (earliest deadline first) 
			sortdtasks = sorted(tasksEndTime.items(),key=operator.itemgetter(1)) 
			print "sorted tasks according to Ealiest Deadline First " , sortdtasks
			#print "current time in seconds : ",currenttimeinseconds
			firstelement = (sortdtasks[0][0])
			tasksDic[firstelement]._TempStartTime = currenttimeinseconds
			tasksDic[firstelement]._TempWorstCaseFinishingTime = currenttimeinseconds + tasksDic[firstelement]._ProcessingRmainingTime
			# calculat the worst case finishing time for each task  Priority,EndTime,ProcessingTime,name)
			for i in range(1,len(tasksDic)):
				currenttask = tasksDic[(sortdtasks[i][0])]
				lasttask = tasksDic[(sortdtasks[i-1][0])]
				currenttask._TempStartTime = lasttask._TempWorstCaseFinishingTime
				currenttask._TempWorstCaseFinishingTime = lasttask._TempWorstCaseFinishingTime + currenttask._ProcessingRmainingTime
			
			# compare worst case finishing time with end time for each task
			for i in range(len(tasksDic)):
				if (tasksDic[(sortdtasks[i][0])]._TempWorstCaseFinishingTime) < (tasksDic[(sortdtasks[i][0])]._EndTime): 
					print (" %s pass guarantee test "% tasksDic[(sortdtasks[i][0])]._Name)
				elif(tasksDic[(sortdtasks[i][0])]._TempWorstCaseFinishingTime) > (tasksDic[(sortdtasks[i][0])]._EndTime): 
					self.__scheduleFail = True
					print (" %s fail in  guarantee test "% tasksDic[(sortdtasks[i][0])]._Name)
					
			# run the stopped task again 
			if (self.__scheduleFail == True):
				for i in range(len(tasksDic)):
					if (tasksDic[(sortdtasks[i][0])]._Status == 'Stopped'):
						tasksDic[(sortdtasks[i][0])]._Status = 'Running'


			if (self.__scheduleFail == False):
				print "no fails scheduling ......"
				for i in range(len(tasksDic)):
					tasksDic[(sortdtasks[i][0])]._StartTime = tasksDic[(sortdtasks[i][0])]._TempStartTime
					tasksDic[(sortdtasks[i][0])]._WorstCaseFinishingTime = tasksDic[(sortdtasks[i][0])]._TempWorstCaseFinishingTime
					tasksDic[(sortdtasks[i][0])]._Status ='Scheduled' # change status to scheduled
						# change the state of first task to running status 
			if(tasksDic[(sortdtasks[0][0])]._StartTime == currenttimeinseconds and tasksDic[(sortdtasks[0][0])]._Status =='Scheduled'):
				tasksDic[(sortdtasks[0][0])]._Status = 'Running' 
			
			#for i in range(len(tasksDic)):
				#print (" %s Temp Start Time :%f, EndTime: %f ,Temp WorstCaseFinishingTime: %f " %(tasksDic[(sortdtasks[i][0])]._Name,tasksDic[(sortdtasks[i][0])]._TempStartTime/3600.0,tasksDic[(sortdtasks[i][0])]._EndTime/3600.0,tasksDic[(sortdtasks[i][0])]._TempWorstCaseFinishingTime/3600.0))

				#print (" %s Start Time :%f, EndTime: %f , WorstCaseFinishingTime: %f " %(tasksDic[(sortdtasks[i][0])]._Name,tasksDic[(sortdtasks[i][0])]._StartTime/3600.0,tasksDic[(sortdtasks[i][0])]._EndTime/3600.0,tasksDic[(sortdtasks[i][0])]._WorstCaseFinishingTime/3600.0))

			#print "End of task Schedule........."


		#user fefined function 
	def taskArrived(self,message):
		tmpmsg = message['data']
		#print message['data']
		#print message['sendername']
		tempint = list(tmpmsg)
		priority = int(tempint[1])
		processingTime =int(tempint[2]+tempint[3]+tempint[4]) * 60 # converted to seconds
		#endTime = int(tempint[5]+tempint[6]+tempint[7]+tempint[8])
		endTime = tempint[5]+tempint[6]+tempint[7]+tempint[8]
		self.__newTask[message['sendername']]= {'priority':priority,'processingTime':processingTime,'endTime':endTime}
		#print "task Queue of the machine  :", tasks
		self.__newTask[message['sendername']]['endTime']=self.converttoseconds(self.__newTask[message['sendername']]['endTime'])
		self.__newTaskArrived = True
		#print "new task to add ", self.__newTask
		self.addNewTask(self.__newTask) # create new task object and add it to the the task queue of the machine 
		if (self.__scheduleFail == False):
			#print("schedule for %s done,start time: %f, End Time: %f"%(self.__taskDic[message['sendername']]._Name,self.__taskDic[message['sendername']]._StartTime/3600.0,self.__taskDic[message['sendername']]._WorstCaseFinishingTime/3600.0))
			response = str(self.__taskDic[message['sendername']]._StartTime) +' '+ str(self.__taskDic[message['sendername']]._WorstCaseFinishingTime)					
			#print response
			self.sendmessage('TCP', message['sendername'],'', 'SCHEDULED', response)

		if(self.__scheduleFail == True):
			del self.__taskDic[message['sendername']]
			response = 'No time for you ,try again later '
			self.sendmessage('TCP', message['sendername'],'', 'SCHEDULEFAIL', response)
		self.__scheduleFail = False
		print "End of thask arrived ................."
		#self.stopRunningTask(self.__taskDic)

	




def main():

	try:
		print "main statrted ....."
		shutdown = [False]
		if len(sys.argv) !=3:
			print "error"
			print"Usage : filename.py <router_ip> <send_name>"
			sys.exit()
		router_ip = sys.argv[1]
		name = sys.argv[2]
		trnasTime = 5
		Type = "machine"
		print "router ip is : ",router_ip
		myInterface = Machine(shutdown,name,Type,router_ip,trnasTime)
	 	myInterface.display_message_list() 
		myInterface.add_handler('ADD', myInterface.taskArrived)

		while not shutdown[0]:
			# save the user's input in a variable
			input_text = raw_input('>>>')
	
			#if the user enters 'EXIT', the inifinte while-loop quits and the
		# program can terminate
			if input_text == 'EXIT':
				shutdown[0] = True
				del myInterface
			elif input_text == 'PRINTQUEUE':
				myInterface.print_elements_queue();
			elif input_text =='SIKO':
				koko = myClass(myInterface.add_handler,myInterface.sendmessage)
	except KeyboardInterrupt:
		shutdown = [True]
		sys.exit()


if __name__ == "__main__":
	main()
