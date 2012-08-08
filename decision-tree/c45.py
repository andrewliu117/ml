#!/usr/bin/env python
# -*- coding: utf-8 -*-

from info_gain_processed import *
import pygraphviz as pgv

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
	def __init__(self):
		self.root = treenode()
		self.feature_set = set()
		self.tdata = None 
		self.threshold = 0.0

	def settdata(self, data):
		self.tdata = data
		self.root.tdata = data

	# use info gain ratio
	def divide_node(self, node, igr_threshold = 0.1):
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
		if max_igr < igr_threshold:
			return
		xlist = map(lambda data:data["x"][max_idx], node.tdata)
		xset = set(xlist)
		div_data = {}
		for data in node.tdata:
			new_data = {"x":[]}
			for i in range(len(data["x"])):
		#		if i != max_idx:
		#			new_data["x"].append(data["x"][i])
				new_data["x"].append(data["x"][i])
			new_data["y"] = data["y"]
			if data["x"][max_idx] in div_data:
				div_data[data["x"][max_idx]].append(new_data)
			else:
				div_data[data["x"][max_idx]] = [new_data]

		node.div_feature = max_idx
	#	print "max_idx", max_idx
		
	#	print "start ----- div_data"
	#	for key1 in div_data.keys():
	#		print key1, div_data[key1]
	#	print "end   ----- div_data"
		
		#node.son = []
		for key in div_data.keys():
	#		print key
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
	#		print "son[1].tdata", son[1].tdata
			if len(son[1].tdata) == 1:
				continue
			y_set = set()
			for data in son[1].tdata:
				y_set.add(data["y"])
				
			if len(y_set) < 2:
				continue
			self.divide_node(son[1], igr_threshold)


	def train(self, igr_threshold = 0.1):
		#print self.root.tdata				
		self.divide_node(self.root, igr_threshold)

	def print_node(self, A, node, node_num, total_num):
		if len(node.son) == 0:
			return total_num
		for son in node.son:
			total_num += 1
			A.add_node(total_num, label = str(son[1].label))
			line_label = "x[%d]=%d" %(node.div_feature, son[0])
			A.add_edge(node_num, total_num, label = line_label) 
			total_num += self.print_node(A, son[1], total_num, total_num)
		return total_num
				
	def print_tree(self, fn):
		A=pgv.AGraph(directed=True,strict=True)
		A.add_node(1, label = str(self.root.label))
		self.print_node(A, self.root, 1, 1)	
		A.layout('dot')
		A.draw(fn)

	# C(T), 损失值
	def	pure_lost(self, node):
		if len(node.son) == 0:
			H = len(node.tdata) * entropy(node.tdata) 
			T = 1
		else:
			H = 0.0
			T = 0
			for son in node.son:
				h, t = self.pure_lost(son[1])
				H += h
				T += t
		return (H, T)
	
	def lost(self, punish_ratio = 0.0):
		pure_lost_value, leaf_nu = self.pure_lost(self.root)
		print "pure_lost_value = %f, leaf_nu = %d" %(pure_lost_value, leaf_nu)	
		return pure_lost_value + punish_ratio * leaf_nu

	def pruning(self, node, punish_ratio = 0.0):
		if len(node.son) == 0:
			return
		need_pruning = True
		for son in node.son:
			if len(son[1].son) != 0:
				self.pruning(son[1], punish_ratio)
				if len(son[1].son) != 0:
					need_pruning = False

		if need_pruning:
			H,T = self.pure_lost(node)
			son_list = node.son
			node.son = []
			H1,T1 = self.pure_lost(node)
			print H, T, H1, T1
			if H + punish_ratio * T < H1 + punish_ratio * T1:  
				node.son = son_list
			else:
				print "pruning it's sons"
		return

	def test(self, node, test_x):
		if len(node.son) == 0:
			return node.label
		else:
			div_val = test_x[node.div_feature]
			for son in node.son:
				if div_val == son[0]:
					return self.test(son[1], test_x)
		return node.label

			

if __name__ == "__main__":
	obj = c45()
	data = process_data()
	obj.settdata(data)
	obj.root.gen_label()
	#print data
	obj.train()
	print "-------after train---------"
	obj.print_tree("c45.png")
	
