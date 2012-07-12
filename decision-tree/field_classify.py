#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import string
import math

def trim(str):
	while (str[0] == " "):
		str = str[1:]
	while (str[-1] == "\n"):
		str = str[0:-1]
	return str

def process_data():
	dataset = []
	ylist = {"Play":1, "Don't Play":0}
	outlook = {"sunny":0, "overcast":1, "rain":2}
	windy = {"true":1, "false":0}
	f = open("golf.data", "r")
	for line in f:
		lf = string.split(line, ",")
		x = {}
		#x["outlook"] = outlook[trim(lf[0])]
		#x["temperature"] = int(lf[1])/5
		#x["humidity"] = int(lf[2])/5
		#x["windy"] =  windy[trim(lf[3])]
		#x["x"] = (outlook[trim(lf[0])], int(lf[1])/5, int(lf[2])/5, windy[trim(lf[3])])
		x["x"] = (outlook[trim(lf[0])], int(lf[1]), int(lf[2]), windy[trim(lf[3])])
		x["y"] = ylist[trim(lf[4])]
		dataset.append(x)
	return dataset

def entropy(ylist):
	H = 0.0
	Dsize = 0
	D = {}
	for y in ylist:
		Dsize += 1
		if y in D:
			D[y] += 1
		else:
			D[y] = 1
	for y in D:
		H += -(float(D[y]) / Dsize) * math.log(float(D[y]) / Dsize)
	return H

def con_entropy(xylist, xi):
	H = 0.0
	Dsize = 0
	D = {}
	for x,y in xylist:
		if x == xi:
			Dsize += 1
			if y in D:
				D[y] += 1
			else:
				D[y] = 1
	for y in D:
		H += -(float(D[y]) / Dsize) * math.log(float(D[y]) / Dsize)
	return H

#def slipt_x(xset, xylist, H,  

def feature_split(xylist, size, a):
	ylist=map(lambda xy: xy[1], xylist)
	ig = entropy(ylist)  
	xlist = map(lambda xy: xy[0], xylist)
	xlist = list(set(xlist))
	xlist.sort()
	#print "xlist ", xlist

	max_ig = 0.0
	split_x = xlist[0]
	for xi in xlist[0:-1]:
		xylist1 = []
		for x,y in xylist:
			if x <= xi:
				xylist1.append((a,y))
			else:
				xylist1.append((a+1,y))
		igs = info_gain(xylist1)
		if max_ig < igs[0]:
			max_ig = igs[0]
			split_x = xi
	
	print "max_ig [%f], split_x [%d]" %(max_ig, split_x)
	ret = {}
	# stop
	if size == 2:
		for xi,y in xylist :
			if xi <= split_x:
				ret[xi] = a
			else: 
				ret[xi] = a+1
		return ret

	# recursion 
	new_xylist1 = []
	new_xylist2 = []
	for x,y in xylist:
		if x <= split_x:
			new_xylist1.append((x,y))
		else:
			new_xylist2.append((x,y))
	
	#print new_xylist1
	#print new_xylist2

	if len(new_xylist1) > 1:
		ret_dict =  feature_split(new_xylist1, size/2, a*2 + 2)
		for key in ret_dict.keys():
			ret[key] = ret_dict[key]
	else:
		for x,y in new_xylist1:
			ret[x] = a

	if len(new_xylist2) > 1:
		ret_dict = feature_split(new_xylist2, size/2, a*2 + 4)
		for key in ret_dict.keys():
			ret[key] = ret_dict[key]
	else:
		for x,y in new_xylist2:
			ret[x] = a + 1
	return ret

def info_gain(xylist):
	ylist = map(lambda xy: xy[1], xylist)
	ig = entropy(ylist)  
	#print "the entropy of data is [%f]" % ig

	Xi = {}
	Dsize = 0
	split_entropy = 0.0;
	for xy in xylist:
		Dsize += 1
		if xy[0] in Xi:
			Xi[xy[0]] += 1
		else:
			Xi[xy[0]] = 1
	for xi in Xi.keys():
		conH = con_entropy(xylist, xi) 
		ig -= float(Xi[xi]) / Dsize * conH
		split_entropy +=  -float(Xi[xi]) / Dsize * math.log(float(Xi[xi]) / Dsize)
	igr = ig/ split_entropy
	return ig, igr


if __name__ == "__main__":
	dataset = process_data()
	print dataset

	names = ["outlook", "temperature", "humidity", "windy"]

	# temperature
	xylist = map(lambda data: (data["x"][1], data["y"]), dataset)
	print xylist
	split_temp = feature_split(xylist, 4, 0)
	for key in split_temp.keys():
		print key, split_temp[key]

	print "---------------------"
	# humidity
	xylist = map(lambda data: (data["x"][2], data["y"]), dataset)
	print xylist
	split_humi = feature_split(xylist, 4, 0)
	for key in split_humi.keys():
		print key, split_humi[key]

	f = open("golf.data_processed", "w")
	for data in dataset:
		x0 = data["x"][0]
		x1 = split_temp[data["x"][1]]
		x2 = split_humi[data["x"][2]]
		x3 = data["x"][3]
		y = data["y"]
		str = "%d\t%d\t%d\t%d\t%d\n" %(x0, x1, x2, x3, y)
		f.write(str)
