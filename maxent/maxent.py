#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math

xlist=[]
ylist=[]
fw = {}

def initdata():
	tf = open("zoo.train", "r")
	for line in tf:
		vlist = line.split(" ")
		y = int(vlist[0][1:])
		ylist.append(y)
		vlist = vlist[1:]
		x = []
		for v in vlist:
			xi = int(v[1:])
			x.append(xi)
		xlist.append(x)
	tf.close()	

	#init feature and weights
	for i in range(len(xlist)):
		for j in range(len(xlist[i])):
			fw[(j, xlist[i][j], ylist[i])] = 0.0

def wf(x, y):
	ret = 0.0
	for (i1, v1, c1) in fw.keys():
		if  v1 == x[i1] and c1 == y:
			ret += fw[(i1, v1, c1)]
	return ret

def z(x):
	ret = 0.0
	for y in ylist:
		Zy = wf(x, y)
		ret += math.exp(Zy)
	return ret

def ep_f(i, v, c):
	ret = 0.0
	for idx in range(len(xlist)):
		if xlist[idx][i] == v and ylist[idx] == c:
			ret += 1.0 / len(xlist)
	return ret

def Px(x):
	num = 0.0
	for x_vec in xlist:
		if x == x_vec:
			num += 1
	return num / len(xlist)

def ep1_f(i, v, c):
	# bugfix for p(x)
	ret = 0.0
	for idx in range(len(xlist)):
		if xlist[idx][i] == v and ylist[idx] == c:
			px = Px(xlist[idx])
			Z = z(xlist[idx])
			P = math.exp(wf(xlist[idx], ylist[idx])) / Z
			ret += px * P / len(xlist) 
	return ret

def likehood():
	lik = 0.0
	for i in range(len(xlist)):
		lik +=  wf(xlist[i], ylist[i]) / len(xlist)
		lik -= math.log(z(xlist[i])) / len(xlist)
	return lik

def train(e):
	dis = 1
	round = 0
	while dis > e:
		delta = []
		for (i, v, c) in fw.keys():
			ep = ep_f(i, v, c)
			ep1 = ep1_f(i, v, c)
			deltai = 1.0 / len(fw) * math.log(ep/ep1)
			delta.append(deltai)
			fw[(i, v, c)] += deltai 

		dis = 0
		for d in delta:
			dis += d * d
		dis = math.sqrt(dis)
		round += 1
		likhood = likehood()
		print "round: %d, dis = %f, likehood = %f" %(round, dis, likhood)

if __name__ == "__main__":
	initdata()
	train(0.00005)
	fr = open("train_ouput", "w")
	for (i, v, c) in fw.keys():
		fr.write("%d\t%d\t%d\t%f" % (i, v, c, fw[(i, v, c)]))
	fr.close()
	print "done!"
	sys.exit(0)
	
