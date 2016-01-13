import xml.etree.ElementTree as etree

#import copy
#import re
#import time
#import numpy as np
#import matplotlib.pyplot as plt
import xml.etree.ElementTree as etree
import sys

import splacris as sc

######################################################################
#                                                                    #
# This file is used to test all methods from Cost and SPLAcris class #
#                                                                    #
######################################################################

if len(sys.argv) != 3:
	print "usage: tester.py <input.xml> <costs.txt>"
	sys.exit()

#I read the input file .....
with open (sys.argv[1], "r") as f:
    xml=f.read()
term = xml


#Need to implement is_spla() and is_cost() to check input files sintax!!!


#We create a cost object and test it..
cost = sc.Cost(sys.argv[2])
print cost.cost
print cost.default
print str(cost.get_cost(["A","C",'D'],'E'))

#We initiate a SPLAcris term
term_initial  = etree.fromstring(term)
trace_initial = []
cost_initial  = 0

#We create a SPLAcris object
fsm = sc.SPLAcris(term_initial,trace_initial,cost_initial)

#Lets test some SPLAcris methods..
print ("Has mand?")
print (str(fsm.has_mand(fsm.term)))

print ("Is feature inside?")
print (str(fsm.is_feature_inside(fsm.term,"NR")))

print ("Is nil inside?")
print (str(fsm.has_nil(fsm.term)))

print ("Is computable?")
print (str(fsm.is_computable(fsm.term,"NN")))

print ("Get computables")
print (str(fsm.get_computables(fsm.term)))

#print ("Compute feature")
#print(etree.tostring(fsm.compute_feature(fsm.term,"checkmark",cost).term))

# print ("Get mand")
# print (str(fsm.get_mand(fsm.term)))
# 
# print ("Is forb?")
# print (str(fsm.is_forb(fsm.term,"q")))
# 
# print ("Is mand?")
# print (str(fsm.is_mand(fsm.term,"q")))
# 
# print ("Is optional?")
# print (str(fsm.is_optional(fsm.term,"M")))
# 
# print ("Check constraints?")
# print(etree.tostring(fsm.check_constraints(fsm.term,"P")))
# 
# print ("Merge consecutive parallels")
# fsm.merge_parallels()
# #print(etree.tostring(fsm.term))
# 
# print ("Merge consecutive choose_1")
# fsm.merge_choose_1()
# #print(etree.tostring(fsm.term))
# 
# print ("Remove choose 1")
# print(etree.tostring(fsm.remove_choose_1(fsm.term,"NT")))
# 
# print ("Remove lonely choose_1")
# print(etree.tostring(fsm.remove_lonely_choose_1(fsm.term)))
# 
# print ("Remove feature")
# print(etree.tostring(fsm.remove_feature(fsm.term,"M")))
# 
# print ("Can tick?")
# print (str(fsm.can_tick(fsm.term)))
