#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import string
import math

def process_data():
	dataset = []
	f = open("golf.data_processed", "r")
	for line in f:
		lf = string.split(line, "\t")
		x = {}
		#x["outlook"] = outlook[trim(lf[0])]
		#x["temperature"] = int(lf[1])/5
		#x["humidity"] = int(lf[2])/5
		#x["windy"] =  windy[trim(lf[3])]
		x["x"] = (int(lf[0]), int(lf[1]), int(lf[2]), int(lf[3]))
		x["y"] = int(lf[4])
		dataset.append(x)
	return dataset

def chi_square(xylist):
	xlist = map(lambda xy: xy[0], xylist)
	xlist = list(set(xlist))
	xlist.sort()
	ylist = map(lambda xy: xy[1], xylist)
	ylist = list(set(ylist))
	ylist.sort()
	#print xlist
	#print ylist

	N = len(xylist)
	Nxy = {}
	Nx = {}
	Ny = {}
	for x,y in xylist:
		#xy = "%d_%d" %(x,y)	
		#Nxy[xy] += 1
		if (x,y) in Nxy:
			Nxy[x,y] += 1
		else:
			Nxy[x,y] = 1

		if x in Nx:
			Nx[x] += 1
		else:
			Nx[x] = 1
		if y in Ny:
			Ny[y] += 1
		else:
			Ny[y] = 1

	#print Nxy
	chi = 0.0
	for x in xlist:
		for y in ylist:
			xy = "%d_%d" %(x,y)	
			Exy = float(Nx[x]*Ny[y]) / N
			if (x,y) not in Nxy:
				Nxy[x,y] = 0
			chi += math.pow(Nxy[x,y] - Exy, 2) / Exy
	return chi
			

if __name__ == "__main__":
	dataset = process_data()
#	print dataset

	names = ["outlook", "temperature", "humidity", "windy"]
	for i in range(len(dataset[0]["x"])):
		xylist = map(lambda data: (data["x"][i], data["y"]), dataset)
		chi_value = chi_square(xylist)
		print "chi square test value of %s : %f" %(names[i], chi_value)
#		sys.exit(0)




