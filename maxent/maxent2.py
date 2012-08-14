#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math

xlist=[]
ylist=[]
fw = {}
ep_dict = {}
g_wf = {}
g_z = {}
ymax = 0

def initdata():
	tf = open("zoo.train", "r")
	for line in tf:
		line = line[:-1]
		vlist = line.split(" ")
		y = int(vlist[0][1:])
		ylist.append(y)
		vlist = vlist[1:]
		x = []
		for v in vlist:
			xi = int(v[-1])
			x.append(xi)
		xlist.append(x)
	tf.close()	

	ymax = 0

	#init feature and weights
	for y in ylist:
		if ymax < y:
			ymax = y

	xmax = xlist[0]
	for x in xlist:
		for i in range(len(x)):
			if xmax[i] < x[i]:
				xmax[i] = x[i]

	for i in range(len(xmax)):
		for v in range(xmax[i]+1):
			for c in range(1, ymax+1):
				fw[(i, v, c)] = 0.0
	return ymax


def wf(xidx, x, yidx, y):
	if (xidx,yidx) in g_wf.keys():
		return g_wf[(xidx, yidx)]
	ret = 0.0
#	for (i1, v1, c1) in fw.keys():
#		if  v1 == x[i1] and c1 == y:
#			ret += fw[(i1, v1, c1)]
	for idx in range(len(x)):
		if (idx, x[idx],y) in fw.keys():
			ret += fw[(idx, x[idx], y)]
	g_wf[(xidx,yidx)] = ret
	return ret

def z(idx, x):
	if idx in g_z.keys():
		return g_z[idx]
	ret = 0.0
	for yidx in range(len(ylist)):
		Zy = wf(idx, x, yidx, ylist[yidx])
		ret += math.exp(Zy)
	g_z[idx] = ret
	return ret

def ep_f_dict():
	for (i, v, c) in fw.keys():	
		ef = 0.0
		for idx in range(len(xlist)):
			if xlist[idx][i] == v and ylist[idx] == c:
				ef += 1.0 / len(xlist)
		if ef == 0.0:
			ef = 0.00000001
		ep_dict[(i,v,c)] = ef

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
		for y in range(1, ymax+1):
			if xlist[idx][i] == v and y == c:
				#px = Px(xlist[idx])
				Z = z(idx, xlist[idx])
				P = math.exp(wf(idx, xlist[idx], yidx, ylist[yidx])) / Z
				#ret += px * P / len(xlist) 
				ret +=  P / len(xlist) 
	return ret

def likehood():
	lik = 0.0
	for i in range(len(xlist)):
		lik +=  wf(i, xlist[i], i, ylist[i]) / len(xlist)
		lik -= math.log(z(i, xlist[i])) / len(xlist)
	return lik

def train(e):
	ep_f_dict()
#	PX()
#	sys.exit(0)
	dis = 1
	round = 0
	while dis > e:
		delta = []
		g_wf = {}
		g_z = {}
		for (i, v, c) in fw.keys():
			ep = ep_dict[(i, v, c)]
			ep1 = ep1_f(i, v, c)
			if ep1 == 0:
				ep1 = 0.00000001
			deltai = math.log(ep/ep1) 
			deltai = deltai / len(fw)
			delta.append(deltai)
			fw[(i, v, c)] += deltai 
			#print i,v,c, deltai

		dis = 0
		for d in delta:
			dis += d * d
		dis = math.sqrt(dis)
		round += 1
		likhood = likehood()
		print "round: %d, dis = %f, likehood = %f" %(round, dis, likhood)

if __name__ == "__main__":
	ymax = initdata()
	print len(fw)
	#sys.exit(0)
	train(0.00005)
	fr = open("train_ouput", "w")
	for (i, v, c) in fw.keys():
		fr.write("%d\t%d\t%d\t%f" % (i, v, c, fw[(i, v, c)]))
	fr.close()
	print "done!"
	sys.exit(0)
	
