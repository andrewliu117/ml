#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import random
import matplotlib.pyplot as plt

if __name__ == "__main__":
	w = -0.6
	b = 80
	samples = []
	negative = 0

	fn = open("svm.train_gen", "w")
	for i in range(0, 30):
		x1 = random.randint(20, 80)
		x2 = random.randint(20, 80)
		label = x2 - (x1 * w + 80) 
		if label > 0:
			if label < 10 and random.randint(0,100) < 30:
				label = -1
			else:
				label = 1
				negative += 1
		else:
			if label > -10 and random.randint(0,100) < 30:
				label = 1
			else:
				label = -1
				negative += 1
		print x1, x2, label
		fn.write("%d\t%d\t%d\n" %(x1, x2, label))
		samples.append((x1, x2, label))
	
	fn.close()	
	print negative

	plt.xlabel(u"x1")
	plt.xlim(0, 100)
	plt.ylabel(u"x2")
	plt.ylim(0, 100)
	plt.title("SVM - Train Data")
	ftrain = open("svm.train_gen", "r")
	for line in ftrain:
		line = line[:-1]
		sam = line.split("\t")
		if int(sam[2]) > 0:
			plt.plot(sam[0],sam[1], 'or')
		else:
			plt.plot(sam[0],sam[1], 'og')
		#plt.plot(sam[0],sam[1], 'ok')

	lp_x1 = [10, 90]
	lp_x2 = []
	lp_x2up = []
	lp_x2down = []
	for x1 in lp_x1:
		lp_x2.append(w * x1 + b)
		lp_x2up.append(w * x1 + b + 5)
		lp_x2down.append(w * x1 + b - 5)
	plt.plot(lp_x1, lp_x2, 'b')
	plt.plot(lp_x1, lp_x2up, 'b--')
	plt.plot(lp_x1, lp_x2down, 'b--')
	plt.show()


