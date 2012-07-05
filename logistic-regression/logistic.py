#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import string
import math
import sys

def process_data():
	dataset = []
	f = open("dataset.txt", "r")
	for line in f:
		if line[0] == "#":
			continue
		l = string.split(line, " ")
		x = []
		for i in l[2:-1]:
			x.append(int(i))
		dataset.append((x,int(l[-1])))
	return dataset

def classify(w, x):
	wx = 0.0;
	for i in range(len(w)):
		wx = wx + w[i] * x[i]	
	return 1/(1.0 + math.exp(-wx))	
	

def training(dataset):
	w = []
	rate = 0.0001
	for i in range(len(dataset[0][0])):
		w.append(0)
	print w
	for round in range(10000):
		loglik = 0.0
		lik = 1.0
		for set in dataset:
			x = set[0]
			y = set[1]
			predict = classify(w, x)
			for j in range(len(w)):
				w[j] = w[j] + rate*(y - predict)*x[j]
			loglik += (y * math.log(classify(w, x)) + (1 - y) * math.log(1 - classify(w, x)))
			lik = lik * classify(w,x) * (1 - classify(w, x))
		print "round %d, w is %s, lik is %f\n" %(round, str(w), loglik)

	return w
	

if __name__ == "__main__":
	dataset = process_data()
	w = training(dataset)
	x = (2, 1, 1, 0, 1)
	print "prob(1|%s) = %f " %(str(x), classify(w,x))
	x = (1, 0, 1, 0, 0)
	print "prob(1|%s) = %f " %(str(x), classify(w,x))
