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
g_ibmatrix = []
g_gw = []
	
def init_globel():
	for i in range(len(g_data.fw)):
		row = []
		for j in range(len(g_data.fw)):
			if i == j:
				row.append(1)
			else:
				row.append(0)
		g_ibmatrix.append(row)
		g_gw.append(0.0)
	
	#for row in g_ibmatrix:
	#	print row
	#sys.exit(0)

def matrix_multi_vector(matrix, vector):
	ret_vector = []
	for i in range(len(matrix)):
		n = 0.0
		for j in range(len(vector)):
			n += matrix[i][j] * vector[j]
		ret_vector.append(n)
	return ret_vector

def vector_multi_matrix(vector, matrix):
	ret_vector = []
	for i in range(len(matrix[0])):
		n = 0.0
		for j in range(len(vector)):
			n += vector[j] * matrix[j][i]
		ret_vector.append(n)
	return ret_vector

def matrix_multi_matrix(matrix, matrix1):
	ret_matrix = []
	for i in range(len(matrix)):
		row = []
		for j in range(len(matrix1[0])):
			n = 0.0
			for k in range(len(matrix1)):
				n += matrix[i][k] * matrix1[k][j] 
			row.append(n)
		ret_matrix.append(row)
	return ret_matrix

def matrix_plus_matrix(matrix, matrix1):
	ret_matrix = []
	for i in range(len(matrix)):
		row = []
		for j in range(len(matrix[0])):
			row.append(matrix[i][j] + matrix1[i][j])
		ret_matrix.append(row)
	return ret_matrix

def vector_multi_vector_matrix(vector, vector1):
	ret_matrix = []
	for i in range(len(vector)):
		row = []
		for j in range(len(vector1)):
			row.append(vector[i] * vector1[j])
		ret_matrix.append(row)
	return ret_matrix

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

def train(e):
	init_globel()
	exp_efi_dict()

	idx = 0
	for (i, v, c) in g_data.fw:
		ep = g_data.exp_efi[(i, v, c)]
		ep1 = ep1_f(i, v, c)
		g_gw[idx] = ep1 - ep
		idx += 1
	gw_edis = 0.0
	for gw in g_gw:
		gw_edis += gw * gw

	gw_edis = math.sqrt(gw_edis)
	if gw_edis < e:  
		return

	round = 0
	while True:
		#print g_gw
		deltak = matrix_multi_vector(g_ibmatrix, g_gw)
		#print deltak
		for i in range(len(deltak)):
			deltak[i] = -0.5 * deltak[i]
		idx = 0
		#print "---g_data---"
		#print g_data.fw
		for (i, v, c) in g_data.fw:
			g_data.fw[(i, v, c)] += deltak[idx] 
			idx += 1
		#print g_data.fw

		idx = 0
		g_gw_next = []
		p_cached.clear()
		for (i, v, c) in g_data.fw:
			ep = g_data.exp_efi[(i, v, c)]
			ep1 = ep1_f(i, v, c)
			g_gw_next.append(ep1 - ep)
			idx += 1

		gw_edis = 0.0
		for gw in g_gw_next:
			gw_edis += gw * gw

		gw_edis = math.sqrt(gw_edis)
		if gw_edis < e:  
			return

		# the method of computiong the inverse of matrix B:
		# http://en.wikipedia.org/wiki/BFGS_method
		yk = [] 
		for i in range(len(g_gw)):
			yk.append(g_gw_next[i] - g_gw[i])

		skT_yk = matrix_multi_vector([deltak], yk) 	
		skT_yk = skT_yk[0]
		#print "---- deltak yk ----"
		#print deltak
		#print yk
		#print skT_yk

		sk = deltak

		ykT_iB_yk = vector_multi_matrix(yk, g_ibmatrix)
		ykT_iB_yk = matrix_multi_vector([ykT_iB_yk],yk)  
		ykT_iB_yk = ykT_iB_yk[0]
		#print ykT_iB_yk
		sk_skT_matrix = vector_multi_vector_matrix(sk, sk)
		factor1 = (skT_yk + ykT_iB_yk) / math.pow(skT_yk, 2)
		#print factor1

		iB_yk_skT = matrix_multi_vector(g_ibmatrix, yk)
		iB_yk_skT = vector_multi_vector_matrix(iB_yk_skT, sk)

		sk_ykT_iB = vector_multi_vector_matrix(sk, yk)
		sk_ykT_iB = matrix_multi_matrix(sk_ykT_iB, g_ibmatrix)

		matrix2 = matrix_plus_matrix(iB_yk_skT, sk_ykT_iB)
		#print matrix2
		#print len(matrix2)
		#print len(matrix2[0])

		for i in range(len(g_ibmatrix)):
			for j in range(len(g_ibmatrix[0])):
				g_ibmatrix[i][j] += factor1 * sk_skT_matrix[i][j] - matrix2[i][j] / skT_yk  

		for i in range(len(g_gw)):
			g_gw[i] = g_gw_next[i]

		round += 1
		likhood = likehood()
		print "round: %d, dis = %f, likehood = %.12f" %(round, gw_edis, likhood)

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
		train(0.00005)
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
