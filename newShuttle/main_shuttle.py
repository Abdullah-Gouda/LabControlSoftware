#--------------------------------- general includes ----------------------------------#
from xml.dom.minidom import parse
import xml.dom.minidom
import sys
import os
import time
import threading 
import time
import datetime
import xml.etree.ElementTree as ET

#-------------------------------- project includes ------------------------------------#
sys.path.append('../common')

from p2p_framework import P2P_Interface
from mysql_class import sqldb
from shuttle import Shuttle
#--------------------------------------------------------------------------------------#
#---------------------------------------- global variables ----------------------------#
# getting Configuration data from config.xml file 
configs_file = ET.parse("../config.xml")	
configs = configs_file.getroot()
# general configs
common_configs = configs.find('common_configs')
router_ip = common_configs.find('router_ip').text
trnasportTime = int(common_configs.find('transport_time').text) * 60 # in seconds

# configs specefic for shuttles
shuttle_configs = configs.find("shuttle_configs")
name = shuttle_configs.find('name').text
Type = shuttle_configs.find('type').text

#get database configs 
db_configs = configs.find("database_configs")
host = db_configs.find('host').text
user = db_configs.find('user').text
passwd = db_configs.find('passwd').text
db = db_configs.find('db_name').text

mydb = sqldb(host,user,passwd,db) 

global_shuttle_container = []
# lock the shuttle container list  in order not to access it at the same time form different threads 
shuttle_container_lock = threading.Lock()
#--------------------------------------------------------------------------------------#

def getCurrentTimeInSeconds(self):
        currenttime = datetime.datetime.now()
        currenttimeinseconds = ( currenttime.hour * 60 + currenttime.minute ) * 60
        return currenttimeinseconds

# thread to track shuttle status (busy or free) and to get data from database
 
def shuttle_status(shutdown,interface,transportTime):
	status_busy = False
	got_job_status = False
	shuttle_created = False
	global global_shuttle_container
	Interface = interface
	Priority = 0 
	Machines_dic ={}
	machine4 = {}
	EndTime = 0
			
        def get_job_from_db(message):
        	print "got response from commander \n"
        	if message['data'] != "Error":
			try:
				print "getting data from database server ....\n"   		
				KA_Nummer = message['data']
				#KA_Nummer = 1000022 # I will get this number from the cmd 
		                sql = "SELECT * FROM kundenauftrag WHERE KA_Nummer = %s " % (KA_Nummer)
		                data = mydb.sqlquery(sql)
		                contractNumber = data["rows"][0]["KA_Nummer"]
		                EndTime =  data["rows"][0]["KA_Termin"]
		                print"KA_Nummer : " , contractNumber
		                print "Auftrag Priority", data["rows"][0]["KA_Prio"]
		                print "End Time: ",EndTime
		                # get arbeitsplan    
		                #process_vorgeange = [data["rows"][0]["UB"],data["rows"][0]["MO"],data["rows"][0]["LA"],data["rows"][0]["EV"],data["rows"][0]["RF"],data["rows"][0]["CH"]]
		                process_vorgeange = [data["rows"][0]["RF"],data["rows"][0]["CH"]]
		                print "process_vorgeange" , process_vorgeange
		                
		                for vorgang in process_vorgeange:
		                        sql = "SELECT * FROM arbeitsvorgang WHERE arbeitsvorgang.AV_Nummer = %s " % (vorgang)
		                        plan = mydb.sqlquery(sql)
		                	print ("Vorgang % d : .... %s\n" % (vorgang,plan))
		                	print "vorgang processing time: ",plan["rows"][0]['AV_Zykluszeit']
		                print "Got data from the database !!\n"
		                got_job_status = True
			except:
			    #currentJob = 0
			    got_job_status = False 
			    errormsg = KA_Nummer+" reset"
			    Interface.sendmessage('TCP', "cmd", "Raspberry", "Error", errormsg)
			    print "db Connection Error"
        	else:
			time.sleep(10)
			got_job_status = False 
			
	Interface.add_handler("newJob", get_job_from_db)
	Interface.add_handler("retry", get_job_from_db)
	
			
	while not shutdown[0]:
               time.sleep(5)
	       if not status_busy :
			# I have to check if the commander in address book or not 
			print "sending request to the cmd ..!!\n"
			Interface.sendmessage('TCP', "cmd", "Raspberry", "getJob", "0")
			
                        # a request should be sent to the cmd to get  KA_Nummer 
                                 
                        #Priority=2
                       # Machines_dic ={'machine_1':{'Name':'machine_1','ProcessingTime':'002'}}
                       # machine4 = {'Name':'machine_4','ProcessingTime':'001'} # montagestation 
                       ##print "Machines_dic : " , Machines_dic
                       # EndTime = "15:30" 
                        #print " expected End Time >> ",EndTime
                        # I am passing 2 to contract number (contract number should be in the range [0 - 9])
                        if  got_job_status:
		                myShuttle = Shuttle(shutdown,Priority,EndTime,Machines_dic,machine4,Interface.add_handler,Interface.sendmessage,Interface.get_address_book,trnasportTime,2)
		                print "myShuttle: "+str(myShuttle)+"\n"
		                if myShuttle:
				        myShuttle.addHandlerFunc('PRINT', myShuttle.print_message) 
				        myShuttle.addHandlerFunc('SCHEDULED',myShuttle.get_EDF_response)
				        myShuttle.addHandlerFunc('SCHEDULEFAIL',myShuttle.schedule_fail)
				        myShuttle.addHandlerFunc('SCHEDULEDM4',myShuttle.get_machine_4_response)
				        myShuttle.addHandlerFunc('SCHEDULEFAILM4',myShuttle.schedule_fail)
				        shuttle_container_lock.acquire()
				        global_shuttle_container.append(myShuttle)
				        shuttle_container_lock.release()
				        print "shuttle container: " ,global_shuttle_container
				        print "shuttle added to the container ...!! "
				        status_busy = True
				      
	       time.sleep(15)
               print" --------------------------------------------------------------"
               if(got_job_status and status_busy):
               		
               	      if(myShuttle.getStatus()):
		               print "the  current Contract finished .....\n"
		               print "deleting the current shuttle object \n"
		               shuttle_container_lock.acquire()
		               del global_shuttle_container[0]
		               shuttle_container_lock.release()
		               del myShuttle
		               print " getting new Contract from database \n"
		               status_busy = False 
		               got_job_status = False
              
               print "shuttle container: " ,global_shuttle_container
             


def main():

	try:
#------------------------------------ INITIALIZATIONS ----------------------------------# 
		global global_shuttle_container 	
			
                print "main statrted ....."
		print "Process ID : ",os.getpid()
		shutdown = [False]
		print "Configuration data:"
		print "\t router_ip: ",	router_ip
		print "\t transport Time: ",trnasportTime							
		print "\t name: ",	name						 
		print "\t type: "	,Type
		
		
		myInterface = P2P_Interface(shutdown,name,Type,router_ip)
		print myInterface
		
		#start shuttle status thread  (to track the status of the shuttle [busy or free])_
		t_shuttle_status = threading.Thread(target = shuttle_status,args=(shutdown,myInterface,trnasportTime,))
		t_shuttle_status.start()

		# use a infinite loop for the user prompting 
		while not shutdown[0]:
	
			# save the users input in a variable
			input_text = raw_input('>>>')
	
			# if the user enters 'EXIT', the inifinte while-loop quits and the
			# program can terminate
			if input_text == 'EXIT':
				shutdown[0] = True
		
			# if the user enters 'ADDR', the address book will be printed in the
			# console
			elif input_text == 'ADDR':
				address_book = myInterface.get_address_book()
				print_address_book(address_book)
	

			elif input_text.startswith('CANCEL'):
				machineslist = myShuttle.get_required_machines_list()
				for machine in machineslist:
					myShuttle.sendMessageFunc('TCP',machine,'','CANCEL','hello')
					myShuttle.sendMessageFunc('TCP',machine4['Name'],'','CANCEL','hello')
			elif input_text.startswith('TIME'):
				print "current time: ",datetime.datetime.now()

			elif input_text.startswith('TARGET'):
				global_shuttle_container[0].get_target_list()
				print "global_shuttle_container[0]",global_shuttle_container

	except :
		print ("Error happened in the main function")
		sys.exit()

	



if __name__ == "__main__":
	main()
