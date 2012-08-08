#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from field_classify import *
from c45 import *

str_value = {"F":0.0, "M":1.0, "f":0.0, "t":1.0, "?":-1.0,  "WEST":0, "STMW":1, "SVHC":2, "SVI":3, "SVHD":4, "other":5}
y_value = {"hyperthyroid":1, "primary hypothyroid":2, "compensated hypothyroid":3, "secondary hypothyroid":4, "negative":5}

g_split_rule = {}

# 参数
devi_size = 8
g_punish_ratio = 10

# 处理数据，将字符串替换为数字
def load_data(filename):
	datas = []
	f = open(filename,"r")
	for l in f:
		x=[]
		y = 0
		fields = l.split(",")
		for xi in fields[:-1]:
			if xi in str_value:
				x.append(str_value[xi])
			else:
				x.append(float(xi))
		y_str = fields[-1]
		y_str = y_str.split(".")[0]
		y = y_value[y_str]
		#print x
		#print y
		#print l
		datas.append({"x":x,"y":y})
	return datas

#	用于测试数据的字段划分 
def add_split_rule(idx, split):
	max = {}
	for key in split.keys():
		if split[key] in max:
			if max[split[key]] < key:
				max[split[key]] = key
		else:
			max[split[key]] = key
	print max
	#print split
	max_value = -100
	rule = {}
	for key in max.keys():
		rule[max[key]] = key
		if max_value < max[key]:
			max_value = max[key]
	#if len(rule) == 1 and rule.keys()[0] == -1:
	#	rule[max_value] = rule[rule.keys()[0]] + 1
	g_split_rule[idx] = (rule, max_value)	
	#print g_split_rule
	#sys.exit(0)

# 使用最大熵的方法划分字段
def devide_data(datas):
	print datas[-1]
	devi_fno = [0, 17, 19, 21, 23, 25, 27, 28]
	for i in range(len(datas[0]["x"])):
		if i in devi_fno: 
			print i
			xylist = map(lambda data: (data["x"][i], data["y"]), datas)
			split = feature_split(xylist, 4)
			add_split_rule(i, split)
			#print xylist
			#print datas[-2]
			#print datas[-1]
			#print "--split--"
			#print split
			for data in datas:
				data["x"][i] = split[data["x"][i]]
			#print datas[-2]
			#print datas[-1]
			#sys.exit(0)	

def devide_test_data(test_datas):
	devi_fno = [0, 17, 19, 21, 23, 25, 27]
	for tdata in test_datas:
		#print "-------devide_test_data--------"
		#print tdata["x"]
		for idx in devi_fno:
			val = tdata["x"][idx]
			rule = g_split_rule[idx]
			keys = rule[0].keys()
			keys.sort()
			min_vals = rule[1] 	
			for vals in keys:
				if val < vals:
					min_vals = vals
					break
			#print rule
			#print min_vals
			#print "idx = %d, value[%f] replace by value[%f]" %(idx, tdata["x"][idx], rule[0][min_vals]) 
			tdata["x"][idx] = rule[0][min_vals]

def stat_test_result(stat_y):
	real = 0
	result = 0
	wrong = 0
	wrong2other = 0

	for tdata in test_data:
		t_result = dt_obj.test(dt_obj.root, tdata["x"])
		real_y = tdata["y"]
		
		if real_y == stat_y:
			real += 1
		if t_result == stat_y:
			result += 1
		if real_y != stat_y and t_result == stat_y:
			wrong += 1
		if real_y == stat_y and t_result != stat_y:
			wrong2other += 1
	
	precision = 0.0
	if result != 0:
		precision = (result - wrong) * 100.0 / result
	recall = 0.0
	if real != 0:
		recall = (real - wrong2other) * 100.0 / real

	for key in y_value.keys():
		if y_value[key] == stat_y:
			y_str = key
	print "for %s, precision is : %.2f%%" % (y_str, precision)
	print "for %s, recall ratio is : %.2f%%" % (y_str, recall)

if __name__ == "__main__":
	sample_data = load_data("hypo.data")
	devide_data(sample_data)

	print "--- print rule----"
	for rule in g_split_rule:
		print rule, g_split_rule[rule]

	#sys.exit(0)	

	test_data = load_data("hypo.test")
	print test_data[-1]
	devide_test_data(test_data)
	print test_data[-1]

	#sys.exit(0)	

	dt_obj = c45()
	dt_obj.settdata(sample_data)
	dt_obj.root.gen_label()
	dt_obj.train(0.1)
	print "-------after train---------"
	dt_obj.print_tree("hypo.png")
	print dt_obj.lost(g_punish_ratio)
	print "########start pruning########"
	dt_obj.pruning(dt_obj.root, g_punish_ratio)
	dt_obj.print_tree("hypo_pruned.png")
	print "########end pruning##########"
	print dt_obj.lost(g_punish_ratio)

	#test
	#test_data = [{'y': 2, 'x': [3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 5, 0.0, 2, 1.0, 3, 1.0, 4, 1.0, 3, 0.0, 2, 5]}]
	for i in [1, 2,3,4,5]:
		stat_test_result(i)
