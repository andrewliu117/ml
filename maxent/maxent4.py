#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math

class g_DATA:
	def __init__(self):
		self.xlist = []
		self.xmax = []
		self.ylist = []
		self.ymax = 0.0
		self.fw = {}
		self.exp_efi = {}

g_data = g_DATA()
p_cached = {}


def load_testdata():
	t_xlist = []
	t_ylist = []
	tf = open("zoo.test", "r")
	for line in tf:
		line = line[:-1]
		vlist = line.split(" ")
		y = int(vlist[0][1:])
		t_ylist.append(y)
		vlist = vlist[1:]
		x = []
		for v in vlist:
			xi = int(v[-1])
			x.append(xi)
		t_xlist.append(x)
	tf.close()	
	return t_xlist, t_ylist

def initdata():
	tf = open("zoo.train", "r")
	for line in tf:
		line = line[:-1]
		vlist = line.split(" ")
		y = int(vlist[0][1:])
		g_data.ylist.append(y)
		vlist = vlist[1:]
		x = []
		for v in vlist:
			xi = int(v[-1])
			x.append(xi)
		g_data.xlist.append(x)
	tf.close()	

	#init feature and weights
	for y in g_data.ylist:
		if g_data.ymax < y:
			g_data.ymax = y

	for xi in g_data.xlist[0]:
		g_data.xmax.append(xi)
	for x in g_data.xlist:
		for i in range(len(x)):
			if g_data.xmax[i] < x[i]:
				g_data.xmax[i] = x[i]

	for i in range(len(g_data.xmax)):
		for v in range(g_data.xmax[i]+1):
			for c in range(1, g_data.ymax+1):
				g_data.fw[(i, v, c)] = 0.0

def exp_efi_dict():
	for (i, v, c) in g_data.fw:	
		ef = 0.0
		for idx in range(len(g_data.xlist)):
			if g_data.xlist[idx][i] == v and g_data.ylist[idx] == c:
				ef += 1.0 
		if ef == 0.0:
			ef = 0.00000001
		ef /= len(g_data.xlist)
		g_data.exp_efi[(i,v,c)] = ef

def WF(x, y):
	ret = 0.0
#	for (i1, v1, c1) in g_data.fw.keys():
#		if  v1 == x[i1] and c1 == y:
#			ret += g_data.fw[(i1, v1, c1)]
	for idx in range(len(x)):
		if (idx, x[idx],y) in g_data.fw.keys():
			ret += g_data.fw[(idx, x[idx], y)]
	return ret

def Zw(x):
	ret = 0.0
	for y in range(1, g_data.ymax+1):
		Zy = WF(x, y)
		ret += math.exp(Zy)
	return ret

def ep1_f(i, v, c):
	ret = 0.0
	for idx in range(len(g_data.xlist)):
		x = g_data.xlist[idx]
		for y in range(1, g_data.ymax+1):
			if x[i] == v and y == c:
				if (idx, y) in p_cached:
					ret += p_cached[(idx, y)]
					continue
				Z = Zw(x)
				P = math.exp(WF(x,y)) / Z
				ret +=  P  
				p_cached[(idx,y)] = P
	return ret / len(g_data.xlist)

def likehood():
	lik = 0.0
	for i in range(len(g_data.xlist)):
		lik +=  WF(g_data.xlist[i], g_data.ylist[i])
		lik -= math.log(Zw(g_data.xlist[i]))
	return lik / len(g_data.xlist)

def train():
	exp_efi_dict()
#	PX()
#	sys.exit(0)
	dis = 1
	round = 0
	not_converg = True
	while not_converg:
		p_cached.clear()
		delta = {}
		for (i, v, c) in g_data.fw:
			ep = g_data.exp_efi[(i, v, c)]
			ep1 = ep1_f(i, v, c)
			if ep1 == 0:
				ep1 = 0.00000001
			deltai = math.log(ep/ep1) 
			#deltai = deltai / len(g_data.fw)
			deltai = deltai / len(g_data.xlist[0])
			delta[(i, v, c)] = deltai
			#g_data.fw[(i, v, c)] += deltai 
			#print i,v,c, deltai

		dis = 0
		not_converg = False
		for (i, v, c) in g_data.fw:
			d = delta[(i, v, c)]
			if abs(d / (g_data.fw[(i, v, c)] + 0.0000001)) >= 0.1:
				not_converg = True
			g_data.fw[(i, v, c)] += d
			dis += d * d
		#print p_cached
		#raw_input("press anykey to continue")
		#print delta
		#raw_input("press anykey to continue")
		#print g_data.fw
		#raw_input("press anykey to continue")
		dis = math.sqrt(dis)
		round += 1
		likhood = likehood()
		print "round: %d, dis = %f, likehood = %.12f" %(round, dis, likhood)

def load_model():
	g_data.fw.clear()
	tf = open("train_output", "r")
	for line in tf:
		line = line[:-1]
		vlist = line.split("\t")
		if len(vlist) == 1:
			g_data.ymax = int(vlist[0])
			continue
		g_data.fw[(int(vlist[0]), int(vlist[1]), int(vlist[2]))] = float(vlist[3])
	tf.close()	

if __name__ == "__main__":
	argv = "train"
	if len(sys.argv) == 2:
		argv = sys.argv[1]
	
	if argv == "train":
		initdata()
		print g_data.xlist
		print g_data.ylist
		print "g_data.xmax"
		print g_data.xmax
		print "g_data.ymax"
		print g_data.ymax
		print len(g_data.fw)
		#sys.exit(0)
		train()
		fr = open("train_output", "w")
		fr.write("%d\n" % g_data.ymax)
		for (i, v, c) in g_data.fw.keys():
			fr.write("%d\t%d\t%d\t%f\n" % (i, v, c, g_data.fw[(i, v, c)]))
		fr.close()
		print "train done!"
		sys.exit(0)
	
	if argv == "test":
		print "max entropy IIS test"
		load_model()
		t_xlist, t_ylist = load_testdata()
		wrong = 0
		for idx in range(len(t_xlist)):
			x = t_xlist[idx]
			real_y = t_ylist[idx]
			Z = Zw(x)
			predict_p = 0.0
			predict_c = 1
			for y in range(1, g_data.ymax+1):
				p = math.exp(WF(x, y))/Z
				if p > predict_p:
					predict_p = p
					predict_c = y
				#print "possibility for class[%d] is: %f" %( y, p)
			#raw_input("press anykey to continue")
			print "x is: %s, real/predict class is: %d/%d, predict possibility: %f " % (str(x), real_y, predict_c, predict_p)
			if real_y != predict_c:
				wrong += 1

		print "predict wrong time is:", wrong
		precision = (1 - float(wrong) / len(t_xlist)) * 100
		print "precision is : %.2f%%" % precision
