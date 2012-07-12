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
	yset = {"Play":1, "Don't Play":0}
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
		x["x"] = (outlook[trim(lf[0])], int(lf[1])/5, int(lf[2])/5, windy[trim(lf[3])])
		x["y"] = yset[trim(lf[4])]
		dataset.append(x)
	return dataset

def entropy(dataset):
	H = 0.0
	Dsize = 0
	D = {}
	for i in dataset:
		Dsize += 1
		if i["y"] in D:
			D[i["y"]] += 1
		else:
			D[i["y"]] = 1
	for y in D:
		H += -(float(D[y]) / Dsize) * math.log(float(D[y]) / Dsize)
	return H

def con_entropy(dataset, xi, idx):
	H = 0.0
	Dsize = 0
	D = {}
	for i in dataset:
		if i["x"][idx] == xi:
			Dsize += 1
			if i["y"] in D:
				D[i["y"]] += 1
			else:
				D[i["y"]] = 1
	for y in D:
		H += -(float(D[y]) / Dsize) * math.log(float(D[y]) / Dsize)
	return H

def info_gain(dataset, H, i):
	ig = H
	Xi = {}
	Dsize = 0
	split_entropy = 0.0;
	for data in dataset:
		Dsize += 1
		if data["x"][i] in Xi:
			Xi[data["x"][i]] += 1
		else:
			Xi[data["x"][i]] = 1
	for xi in Xi.keys():
		conH = con_entropy(dataset, xi, i) 
		ig -= float(Xi[xi]) / Dsize * conH
		split_entropy +=  -float(Xi[xi]) / Dsize * math.log(float(Xi[xi]) / Dsize)
	#	print ig, split_entropy
	#sys.exit(0)
	igr = ig/ split_entropy
	return ig, igr


if __name__ == "__main__":
	dataset = process_data()
	print dataset
	H = entropy(dataset)
	print "the entropy of data is [%f]" % H

	names = ["outlook", "temperature", "humidity", "windy"]
	for i in range(len(dataset[0]["x"])):  
		igs = info_gain(dataset, H, i)
		print "info gain and ratio for %s ---" %(names[i])
		print "ig  is [%f]" %(igs[0])
		print "igr is [%f]" %(igs[1])
