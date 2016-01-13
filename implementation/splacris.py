#!/usr/bin/python

#################################################################
# -*- coding: utf-8 -*-                                         #
# Generate the documentation using: epydoc --pdf splacris.py -v #
#                                                               #
# Main class file for                                           #
#    Cost                                                       #
#    SPLAcris                                                   #
#                                                               #
#################################################################

import xml.etree.ElementTree as etree	#To create/use/print trees
import copy								#To copy trees
import re								#For the cost file regular expression processing 
import time								#To calculate execution times


class Cost:
	"""
	This class loads the cost table to a Python hash table
	the hash is <feature><trace list>
	i.e. "F["K","L","U"]":5.5
	"""
	
	#Checked and used
	def __init__(self,cost_file):
		"""
		Constructor method for Cost class , This method
		instance a cost object

		@type self:  Cost instance
		@param self: the cost table instance
		
		@type cost_file: string
		@param cost_file: Cost table file
				
		@rtype: Cost object
		@return: A Cost object
		"""
		self.cost = {}
		with open(cost_file) as f:
			for line in f:	
				feature = re.findall(r'\[([^]]*)\]',line)[0]
 				trace = str(re.findall(r'\[([^]]*)\]',line)[1])
 				trace = trace.split(",")
 				if trace == ['']:
 					trace = []
 					
				value = float(line.split(':')[1])
 				if feature == '*':
 					self.default = value
 				else:	
					self.cost[feature+str(trace)] = value

	#Checked and used
	def get_cost(self,trace,feature):
		"""
		Function to get the cost of compute a
		feature given the previously computed
		features

		@type self:  Cost instance
		@param self: the current Cost instance
		
		@type trace: list
		@param trace: The features trace

		@type feature: string
		@param feature: The produced feature
		
		@rtype: float 
		@return: The cost of compute the feature
		"""
	
		if self.cost.get(feature+str(trace)):	
			return self.cost.get(feature+str(trace))
		else:
			return self.default
			
class SPLAcris:
	"""
	This class defines the SPLAcris cost function
	In this case a SPLAcris object will represent a state in the
	FSM
	"""

	#Checked and used
	def __init__(self,term,trace,cost,itime, etime,uthreshold, lthreshold):
		"""
		Constructor method for SPLAcris class , This method
		instance a SPLAcris object

		@type self:  SPLAcris instance
		@param self: the current SPLAcris instance
		
		@type term: etree SPLAcris term
		@param term: Current SPLAcris term

		@type trace: string
		@param trace: Computed trace to generate current term
		
		@type cost: integer
		@param cost: Cost to generate current trace

		@type itime: time
		@param itime: Initial time

		@type etime: time
		@param etime: End time

		@type uthreshold: float
		@param uthreshold: Upper threshold

		@type lthreshold: float
		@param lthreshold: Lower threshold
		
		@rtype: SPLAcris object
		@return: A SPLAcris object
		"""
		

		self.term = term
		self.trace = trace
		self.cost = cost
		self.itime = itime
		self.etime = etime
		self.uthreshold = uthreshold
		self.lthreshold = lthreshold

	#Checked and used
	def check_syntax(self):
		"""
		Function to check the term syntax

		@type self:  SPLAcris instance
		@param self: the current SPLAcris instance
		
		@rtype: integer 
		@return: 1 if is good 0 if bad
		"""

		for item in self.term.getiterator():				
			if	not (item.tag == "xml" or item.tag == "requires" or item.tag =="excludes" or item.tag =="mand" or item.tag =="forb" or item.tag =="mandatory_feature"  or item.tag =="optional_feature" or item.tag =="choose_1"  or item.tag =="parallel" or item.tag =="checkmark"):
				return 0
 			
			if item.tag == "mandatory_feature" and item.attrib.get("name") == None:
				return 0

			if item.tag == "optional_feature" and item.attrib.get("name") == None:
				return 0
 				
			if item.tag == "excludes" and (item.attrib.get("feature_1") == None or item.attrib.get("feature_2") == None):
				return 0

			if item.tag == "requires" and (item.attrib.get("feature_1") == None or item.attrib.get("feature_2") == None):
				return 0
 				
			if item.tag == "mand" and item.attrib.get("feature") == None:
				return 0	
 				
			if item.tag == "forb" and item.attrib.get("feature") == None:
				return 0	
 									
		return 1
							
	#Checked and used
	def check_constraints(self,tree_original,feature):
		"""
		Function to check if a constraint can be computed
		this method returns a tree with the contraint computed

		@type self:  SPLAcris instance
		@param self: the current SPLAcris instance
		
		@type tree_original: etree
		@param tree_original: The actual SPLA term

		@type feature: string
		@param feature: The produced feature (to check the constraint)
		
		@rtype: etree SPLAcris term
		@return: The new tree with the constraint computed if applies
		"""

		tree= copy.deepcopy(tree_original)
		for parent in tree.getiterator():
			for child in list(parent):				
				if child.tag =="requires" and child.attrib.get("feature_1") == feature:
					child.tag = "mand"
					child.set('feature', child.attrib.get("feature_2"))
					del child.attrib["feature_1"]
					del child.attrib["feature_2"]
				if child.tag =="excludes" and child.attrib.get("feature_1") == feature:
					child.tag = "forb"
					child.set('feature', child.attrib.get("feature_2"))
					del child.attrib["feature_1"]
					del child.attrib["feature_2"]
				if child.tag =="excludes" and child.attrib.get("feature_2") == feature:
					child.tag = "forb"
					child.set('feature', child.attrib.get("feature_1"))
					del child.attrib["feature_1"]
					del child.attrib["feature_2"]						
				if child.tag =="mand" and child.attrib.get("feature") == feature:
					parent.remove(child)
					parent.extend(child)				
					
		return tree

	#Checked and used
	def is_forb(self,tree,feature):
		"""
		Function to check if a feature is forbidden
		this method returns 1 if the feature is 
		forbidden, 0 otherwise

		@type self:  SPLAcris instance
		@param self: the current SPLAcris instance
		
		@type tree: etree
		@param tree: The actual SPLA term

		@type feature: string
		@param feature: The produced feature
		
		@rtype: integer 
		@return: 1 if is forbidden 0 otherwise
		"""
		
		for parent in tree.getiterator():
			if parent.tag =="forb" and parent.attrib.get("feature") == feature:
				return 1
		return 0

	#Checked but not used
	def is_mand(self,tree,feature):
		"""
		Function to check if a feature is mandatory
		this method returns 1 if the feature is 
		mandatory, 0 otherwise

		@type self:  SPLAcris instance
		@param self: the current SPLAcris instance
		
		@type tree: etree
		@param tree: The actual SPLA term

		@type feature: string
		@param feature: The produced feature
		
		@rtype: integer 
		@return: 1 if is forbidden 0 otherwise
		"""
		
		for parent in tree.getiterator():
			if parent.tag =="mand" and parent.attrib.get("feature") == feature:
				return 1
		return 0

	#Checked and used
	def is_optional(self,tree,feature):
		"""
		Function to check if a feature is optional

		@type self:  SPLAcris instance
		@param self: the current SPLAcris instance
		
		@type tree: etree
		@param tree: The actual SPLA term

		@type feature: string
		@param feature: searched feature
		
		@rtype: integer 
		@return: 1 if optional 0 otherwise
		"""
		
		for parent in tree.getiterator():
			if parent.tag=="optional_feature" and parent.attrib.get('name')== feature:
				return 1
		return 0
		
	#Checked and used			
	def is_feature_inside(self,tree,feature):
		"""
		Function to check if a feature is inside
		the term

		@type self:  SPLAcris instance
		@param self: the current SPLAcris instance
		
		@type tree: etree
		@param tree: The actual SPLA term

		@type feature: string
		@param feature: searched feature
		
		@rtype: integer 
		@return: 1 if is found 0 otherwise
		"""
		
		for parent in tree.getiterator():
			if parent.attrib.get('name') == feature:
				return 1
		return 0

	#Checked and used
	def has_nil(self,tree):
		"""
		Function to check if the term has nil inside

		@type self:  SPLAcris instance
		@param self: the current SPLAcris instance
		
		@type tree: tree
		@param tree: The actual SPLA term
		
		@rtype: integer
		@return: 1 if a nil is found, 0 otherwise
		"""
		
		for parent in tree.getiterator():
			if parent.tag == "nil":
				return 1
		return 0

	#Checked and used	
	def is_computable(self,tree,feature):
		"""
		Function to check if a feature is computable

		@type self:  SPLAcris instance
		@param self: the current SPLAcris instance
		
		@type tree: etree
		@param tree: The actual SPLA term

		@type feature: string
		@param feature: searched feature
		
		@rtype: integer 
		@return: 0 if is not computable 1 otherwise
		"""

		for parent in tree.getiterator():
			for child in list(parent):
				if child.tag == "mandatory_feature" or child.tag == "optional_feature":
					for subchild in list(child):
						if self.is_feature_inside(subchild,feature) == 1:
							return 0
		return 1

	#Checked and used	
	def is_computed(self,trace,feature):
		"""
		Function to check if a feature was computed

		@type self:  SPLAcris instance
		@param self: the current SPLAcris instance
		
		@type trace: list
		@param trace: Computed features

		@type feature: string
		@param feature: searched feature
		
		@rtype: integer 
		@return: 0 if was not computed 1 if yes
		"""

		if feature in trace:
			return 1
		else:
			return 0

	#Checked and used
	def has_mand(self,tree):
		"""
		Function to check if a term has mand features
		this method returns 1 if has mand features,
		0 otherwise

		@type self:  SPLAcris instance
		@param self: the current SPLAcris instance
		
		@type tree: etree
		@param tree: The actual SPLA term
		
		@rtype: integer
		@return: 1 if is has mand features 0 otherwise
		"""
		
		for parent in tree.getiterator():
			if parent.tag =="mand":
				return 1
		return 0	
	
	#Checked and used
	def get_mand(self,tree):
		"""
		Function to get the mand features list
		this method returns a list of mand features

		@type self:  SPLAcris instance
		@param self: the current SPLAcris instance
		
		@type tree: etree
		@param tree: The actual SPLA term
		
		@rtype: list
		@return: a list with mand features
		"""
		
		features =[]
		for parent in tree.getiterator():
			if parent.tag =="mand":
				features.append(parent.attrib.get("feature"))
		return features		

	#Checked and used
	def get_forb(self,tree):
		"""
		Function to get the forb features list
		this method returns a list of forb features

		@type self:  SPLAcris instance
		@param self: the current SPLAcris instance
		
		@type tree: etree
		@param tree: The actual SPLA term
		
		@rtype: list
		@return: a list with forb features
		"""
		
		features =[]
		for parent in tree.getiterator():
			if parent.tag =="forb":
				features.append(parent.attrib.get("feature"))
		return features		

	#Checked and used
	def is_blocked(self,tree):
		for m in self.get_mand(tree):
			if self.is_forb(tree,m):
				return 1
		for f in self.get_forb(tree):
			if self.is_mand(tree,f):
				return 1
		return 0
		
	#Checked and used - Modificada para devolver tambien si puedo hacer checkmark
	def get_computables(self, tree):
		"""
		Function to get the computables list

		@type self:  SPLAcris instance
		@param self: the current SPLAcris instance
		
		@type tree: etree
		@param tree: The actual SPLA term
		
		@rtype: list 
		@return: list with computables features
		"""
		
		features=[]
		for parent in tree.getiterator():
			if self.is_computable(tree,parent.attrib.get('name')) and (parent.tag == "mandatory_feature" or parent.tag == "optional_feature" ):
				features.append(parent.attrib.get('name'))
		#Now check if can tick/checkmark as it can be a computable feature
		aux=0
		computables = features
		#print computables
		for fea in computables:
			if self.is_optional(tree,fea):
				aux =aux +1
		if not aux != len(computables) or self.has_nil(tree):
			features.append("checkmark")
		return features
		
	#Checked and used
	def merge_parallels(self):
		"""
		Function to merge consecutive parallels in order to be able to process the term

		@type self:  SPLAcris instance
		@param self: the current SPLAcris instance
		
		@rtype: boolean
		@return: 1 if parallels were merge, 0 otherwise
		"""
		
		removed =0
		for parent in self.term.getiterator():
			if parent.tag == "parallel":
				for child in list(parent):
					if child.tag == "parallel":
						parent.remove(child)
						parent.extend(child)
						removed = 1
		if removed ==0:
			return 0
		else:
			self.merge_parallels()

	#Checked and used
	def merge_choose_1(self):
		"""
		Function to merge consecutive choose_1 in order to be able to process the term

		@type self:  SPLAcris instance
		@param self: the current SPLAcris instance
		
		@rtype: boolean
		@return: 1 if choose_1 were merge, 0 otherwise
		"""
		
		removed =0
		for parent in self.term.getiterator():
			if parent.tag == "choose_1":
				for child in list(parent):
					if child.tag == "choose_1":
						parent.remove(child)
						parent.extend(child)
						removed = 1
		if removed ==0:
			return 0
		else:
			self.merge_choose_1()

	#Checked and used
	def remove_choose_1(self,tree_original, feature):
		"""
		Function to remove features inside the choose_1 operator and leave the feature to be computed with the choose_1

		@type self:  SPLAcris instance
		@param self: the current SPLAcris instance
		
		@type tree_original: etree SPLAcris term
		@param tree_original: The source tree
		
		@type feature: string
		@param feature: The feature which indicates which choose_1 must be removed
		
		@rtype: etree SPLAcris term
		@return: An etree object without the choose_1 operator
		"""
		
		tree= copy.deepcopy(tree_original)
		for parent in tree.iter("choose_1"):
			for child in list(parent):
				if self.is_feature_inside(child,feature) == 0 and self.is_feature_inside(parent,feature) ==1:
					parent.remove(child)
		return tree

	#Checked and used
	def remove_lonely_choose_1(self,tree_original):
		"""
		Function to remove lonely choose_1 relationships

		@type self:  SPLAcris instance
		@param self: the current SPLAcris instance
		
		@type tree_original: etree
		@param tree_original: The actual SPLA term
		
		@rtype: etree 
		@return: tree without lonely choose_1 relationships
		"""
		
		tree= copy.deepcopy(tree_original)
		for parent in tree.getiterator():
			for child in list(parent):				
				if child.tag =="choose_1" and len(child) == 1:
					parent.remove(child)
					parent.extend(child)
		return tree

	#Checked and used
	def remove_feature(self,tree_original, feature):
		"""
		Function to produce a feature, receives a term and a feature to be extracted and returns the term without the feature

		@type self:  SPLAcris instance
		@param self: the current SPLAcris instance
		
		@type tree_original: etree SPLAcris term 
		@param tree_original: The source tree
		
		@type feature: string
		@param feature: The feature to be removed
		
		@rtype: etree SPLAcris term 
		@return: An etree object without the feature
		"""
		
		tree= copy.deepcopy(tree_original)
		for parent in tree.getiterator():
			for child in list(parent):
				if child.attrib.get('name') == feature:
					parent.remove(child)
					parent.extend(child)
					return tree		

	#Checked and used in fsm not anymore
	def can_tick(self,term):
		"""
		Function to check if a term can tick
		It will check for:
		TICK - OFEAT2 - CON3 - REQ3 - EXCL4 - FORB2 - MAND1

		@type self:  SPLAcris instance
		@param self: the current SPLAcris instance
		
		@type term: etree
		@param term: The actual SPLA term
		
		@rtype: integer 
		@return: 1 if can tick  0 otherwise
		"""
		aux=0
		computables = self.get_computables(term)
		for fea in computables:
			if self.is_optional(term,fea):
				aux =aux +1
		if aux != len(computables) or self.has_mand(term) or self.has_nil(term):
			return 0
		else:
			return 1
		
	#Testing pending and used									
	def compute_feature(self, tree_original, feature, cost_table):
		"""
		Function to compute a feature,
		receives a SPLAcris instance, a feature to be computed and a cost table

		@type self:  SPLAcris instance
		@param self: the current SPLAcris instance
		
		@type tree_original: etree SPLAcris term 
		@param tree_original: The source tree
		
		@type feature: string
		@param feature: The feature to be removed

		@type cost_table: A cost function object
		@param cost_table: The cost table
				
		@rtype: SPLAcris 
		@return: A SPLAcris object
		"""
		#Here i need to compute the feature and return a new state for the FSM
		#Lets calculate the new term
		
		new_term = copy.deepcopy(tree_original)
		new_trace = copy.deepcopy(self.trace)
		new_cost = self.cost
		
		if (self.is_forb(new_term,feature) == 0) and (self.is_blocked(new_term) == 0):
			if feature == "checkmark":
				#Aqui incluyo al terminar de computar una traza, aquellos features que
				#No hayan sido computados pero sean mand y no esten prohibidos
				for manda in self.get_mand(new_term):
					if not self.is_forb(new_term,manda):
						new_trace.append(manda)
						new_cost = self.cost + cost_table.get_cost(self.trace,manda)
				new_term = etree.Element("nil")
				new_trace.append(feature)
				new_state = SPLAcris(new_term,new_trace,new_cost,self.itime,time.clock(),self.uthreshold,self.lthreshold)

				#Here thresholds validations
				if new_state.cost < self.lthreshold:
					return None
				if new_state.cost > self.uthreshold:
					return None

				return new_state
			else:
				#print "no prohibido"
				#Checking constraints..
				new_term = self.check_constraints(new_term, feature)
			
				#Checking regular relationships
				new_term = self.remove_choose_1(new_term,feature)
				new_term = self.remove_lonely_choose_1(new_term)
				new_term = self.remove_feature(new_term,feature)
		
				#Compute the new trace
				new_trace.append(feature)
		
				#Compute the new cost
				new_cost = self.cost + cost_table.get_cost(self.trace,feature)

				#We create a SPLAcris object to model a new state
				new_state = SPLAcris(new_term,new_trace,new_cost,self.itime,0,self.uthreshold,self.lthreshold)
				new_state.merge_choose_1()
				new_state.merge_parallels()

				#Here thresholds validation
				if new_state.cost > self.uthreshold:
					return None

				return new_state
		else:
			return None
