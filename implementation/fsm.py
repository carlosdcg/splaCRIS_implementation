#!/usr/bin/python
# -*- coding: utf-8 -*-
#Generate the documentation using: epydoc --pdf splacris.py -v
#Run with scoop 
#sudo python -m scoop -n 4 fsm.py term.xml costs.txt 4
#	-m scoop	Mandatory Uses SCOOP to run program
#	-n 4		Launch a total of 4 worker
#	hostfile	hosts is a file containing a list of host to launch SCOOP
#	-vv			Double verbosity flag.
#	Last number idem than -n 4 its the workers number you can omit this number
#	but the graphic will be generated without the workers number




import xml.etree.ElementTree as etree
import time
import numpy as np
import matplotlib
#Sometimes, if you dont have a graphic interface to be able to use matplotlib, you must force to use Agg (Servers, clusters use)
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import xml.etree.ElementTree as etree
from xml.etree.ElementTree import ParseError
import sys
import splacris as sc
import multiprocessing
import platform
from scoop import futures
import os


def calc_states(state, cost_table,depth=0):
	"""
	Recursive function to generate the Finite State Machine with all posible states, among then, all valid products.

	@type state:  SPLAcris instance
	@param state: The SPLAcris instance
	
	@type cost:  Cost instance
	@param cost_table: The Cost instance to calculate features cost
	
	@rtype: none
	@return: none
	"""
	states_list = []
	futures_list = []
	for feature in state.get_computables(state.term):
		new_state = state.compute_feature(state.term,feature,cost_table)
		if new_state != None:
			if new_state.has_nil(new_state.term):
				#print "Terminal state"
				states_list.append(new_state)
			else:
				#We make a recursive call with scoop (testing parallelism with scoop)
				# Using a max deep of 3 for the tree
				if depth < 1:
					#states_list.extend(futures.submit(calc_states,new_state,cost_table, depth+1).result())
					futures_list.append(futures.submit(calc_states,new_state,cost_table, depth+1))
				else:
					states_list.extend(calc_states(new_state,cost_table, depth+1))

	for fu in futures_list:
		states_list.extend(fu.result())

	return states_list



def main():
######################################
## Begin main section of the script ##
######################################

	#############################
	# Begin initial validations #
	#############################
	
	#Validating script parameters
	if len(sys.argv) != 4:
		print "usage: tester.py <input.xml> <costs.txt> <workers>"
		sys.exit()
	
	#Reading the XML term file
	with open (sys.argv[1], "r") as f:
		xml=f.read()
	term = xml

	#Try to parse the term file into an etree object
	try:
		#We initiate a SPLAcris term
		term_initial  = etree.fromstring(term)
		trace_initial = []
		cost_initial  = 0

	except ParseError:
		print "XML input parsing problem"
		sys.exit()
		
	try:
		workers= sys.argv[3]
	except IndexError:
		workers="NaN"
		sys.exit()
		

	#Costs theresholds for computing products
	uthreshold = 999999999999999999999999999999999999 #Max cost
	lthreshold = 1 #Min cost

	#We create a cost function instance
	cost_table = sc.Cost(sys.argv[2])
	
	
	init_time = time.clock()
	#We create a SPLAcris object
	fsm = sc.SPLAcris(term_initial,trace_initial,cost_initial,init_time,0,uthreshold,lthreshold)

	#If initial term has nil inside
	if fsm.has_nil(term_initial):
		print "Initial term should not have <nil/> inside..."
		sys.exit()
	
	#If all syntax elements are correct
	if fsm.check_syntax() == 0:
		print "Problem with the term syntax"
		sys.exit()		
	
	###########################
	# End initial validations #
	###########################


	#######################
	# Begin SPLAcris call #
	#######################
	
	fsm.itime = time.clock()
	sol = calc_states(fsm,cost_table)
	exec_time=time.clock()-init_time

	#####################
	# End SPLAcris call #
	#####################
	

	########################
	# Begin output results #
	########################	


		
		
	#Ill print the traces and costs for each valid product
	states_time=[]

	for a in sol:
		print a.itime
		print a.etime
		print "-----"

	print ("total products: "+str(len(sol)))
	print ("exec time: "+str(exec_time))

	with open(sys.argv[1]+"_"+sys.argv[2]+"_traces_output.txt", "a") as mytracesfile:
	#	mytracesfile.write( "------------------------------------------\n")
		
	 	for state in sol:
			states_time.append(state.etime - state.itime)
			mytracesfile.write(str(state.trace)+"\n")
			mytracesfile.write(str(state.cost)+"\n")

	#CPU speed
	#cpu_speed = "0"
	#if "Darwin" in str(platform.version()):
	#	cpu_speed = os.popen("sysctl -n machdep.cpu.brand_string").read()
	#else:
	#	cpu_speed = os.popen("grep 'model name' /proc/cpuinfo").read()


	#with open(sys.argv[1]+"_"+sys.argv[2]+"_text_output.txt", "a") as myfile:
    
	#	myfile.write( "------------------------------------------\n")
	#	myfile.write( "Platform:"+str(platform.platform())+"\n")
	#	myfile.write( "Processor:"+str(platform.processor())+"\n")
	#	myfile.write( "Uname:"+str(platform.uname())+"\n")
	#	myfile.write( "System:"+str(platform.system())+"\n")
	#	myfile.write( "Node:"+str(platform.node())+"\n")
	#	myfile.write( "Release:"+str(platform.release())+"\n")
	#	myfile.write( "Version:"+str(platform.version())+"\n")
	#	myfile.write( "Machine:"+str(platform.machine())+"\n")
	#	myfile.write( "CPU speed:"+str(cpu_speed)+"\n")
	#	myfile.write( "CPU count:"+str(multiprocessing.cpu_count())+"\n")
	#	myfile.write( "Computing using # workers:"+str(workers)+"\n")
	#	myfile.write( "Total products:"+str(len(states_time))+"\n")
	#	myfile.write( "Total execution time:"+str(exec_time)+"\n")
	#	#myfile.write( "Average product computing:"+str(np.average(states_time))+"\n")
	
	
	#Ill print a cumulative table for products computing
	x = np.arange(1,len(sol)+1)
	y = states_time
 	plt.xlim(0,len(sol)+1)
	plt.ylim(0,states_time[-1]+states_time[0])
	plt.xlabel('product number')
	plt.ylabel('time to get the product (seconds)')
	plt.plot(x,y,'ro',markersize=3)
	plt.savefig(sys.argv[1]+"_"+sys.argv[2]+"_"+workers+'_graphic_output.eps')
	plt.show()

	######################
	# End output results #
	######################
			
######################################
## End main section of the script ##
######################################



if __name__ == "__main__":
    main()
    
    
