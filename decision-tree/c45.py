#!/usr/bin/env python
# -*- coding: utf-8 -*-

from info_gain_processed import *

class treenode:
	#label = None
	#tdata = None
	#son = []
	#div_feature = 0
	def __init__(self):
		self.label = None
		self.tdata = None
		self.son = []
		self.div_feature = 0
		self.div_value = 0

	
	def setleft(self, left):
		self.left = left
	def setright(self, right):
		self.right = right
	def setlabel(self, label):
		self.label = label
	def gen_label(self):
		y_map = {}
		for data in self.tdata:
			if data["y"] in y_map:
				y_map[data["y"]] += 1
			else:
				y_map[data["y"]] = 1

		label_count = 0

		for ykey in y_map.keys():
			if y_map[ykey] > label_count:
				label_count = y_map[ykey]
				self.label = ykey

class c45:
	root = treenode()
	feature_set = set()
	tdata = None 
	threshold = 0.0

	def settdata(self, data):
		self.tdata = data
		self.root.tdata = data
	
	def divide_node(self, node):
	#	print "here is tdata", node.tdata
		H = entropy(node.tdata)
	#	print H
		max_igr = 0.0
		max_idx = 0
		for i in range(len(node.tdata[0]["x"])):
			ig,igr = info_gain(node.tdata, H, i)
			if igr > max_igr:
				max_igr = igr
				max_idx = i
		xlist = map(lambda data:data["x"][max_idx], node.tdata)
		xset = set(xlist)
		div_data = {}
		for data in node.tdata:
			new_data = {"x":[]}
			for i in range(len(data["x"])):
				if i != max_idx:
					new_data["x"].append(data["x"][i])
			new_data["y"] = data["y"]
			if data["x"][max_idx] in div_data:
				div_data[data["x"][max_idx]].append(new_data)
			else:
				div_data[data["x"][max_idx]] = [new_data]

		node.div_feature = max_idx
		print "max_idx", max_idx
		
	#	print "start ----- div_data"
	#	for key1 in div_data.keys():
	#		print key1, div_data[key1]
	#	print "end   ----- div_data"
		
		#node.son = []
		for key in div_data.keys():
			print key
			son_node = treenode()  
			son_node.tdata = div_data[key]
			son_node.gen_label()
			son_node.div_value = key
			node.son.append((key, son_node))

		#	print "son_node.tdata", son_node.tdata
		#	if len(son_node.tdata) == 1:
		#		continue
		#	y_set = set()
		#	for data in son_node.tdata:
		#		y_set.add(data["y"])
		#		
		#	if len(y_set) < 2:
		#		continue
		#	self.divide_node(son_node)

		for son in node.son:
			print "son[1].tdata", son[1].tdata
			if len(son[1].tdata) == 1:
				continue
			y_set = set()
			for data in son[1].tdata:
				y_set.add(data["y"])
				
			if len(y_set) < 2:
				continue
			self.divide_node(son[1])


	def train(self):
		print self.root.tdata				
		self.divide_node(self.root)

	def print_node(self, node, str):
		if len(node.son) == 0:
			print "%s -- div_value = %d --> node[(label = %d)]"%(str, node.div_value, node.label)
		if str == "root":
			node_str = "node[%s (label = %d, div_feature_idx = %d)]" %(str,  node.label, node.div_feature)
		else:
			node_str = "%s -- div_value = %d --> node[(label = %d, div_feature_idx = %d)]" %(str, node.div_value, node.label, node.div_feature)
		for son in node.son:
			self.print_node(son[1], node_str)
				
	def print_tree(self):
		str = "(%s, label:%d, div_feature_idx:%d)"%("root", self.root.label, self.root.div_feature)
		self.print_node(self.root, "root")	

if __name__ == "__main__":
	obj = c45()
	data = process_data()
	obj.settdata(data)
	obj.root.gen_label()
	print data
	obj.train()
	print "-------after train---------"
	obj.print_tree()
	
	#print "obj.root.son"
	#print obj.root.son
	#print "obj.root.son[0][1].son"
	#print obj.root.son[0][1].son
	#print "obj.root.son[1][1].son"
	#print obj.root.son[1][1].son
	#print "obj.root.son[2][1].son"
	#print obj.root.son[2][1].son
	

