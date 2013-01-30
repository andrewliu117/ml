#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Pegasos inplemented in Python

import os
import sys
import math

G_WEIGHT = []

def parse_image(path):
    img_map = []
    fp = open(path, "r") 
    for line in fp:
        line = line[:-2]
        for ch in line:
            img_map.append(int(ch))
#    print img_map
#    for i in range(32):
#        for j in range(32):
#            print img_map[i*32+j],
#        print " "
#    sys.exit(0)
    return img_map

def predict(model, data):
    ret = 0
    for i in model:
        ret += model[i]*data[i]
    return i

def train_one_model(data, label, sampleNum, modelNum):
    pvalue = predict(G_WEIGHT[modelNum], data)
    if pvalue * label > 0:
        return
    
    # update model
    lambd = 10 
    new_weight = []
    for i in G_WEIGHT[modelNum]:
        new_weight.append(G_WEIGHT[modelNum][i] * ( 1 - 1/sampleNum) + (1 / (lambd * sampleNum))*label*data[i])

    # projection
    norm2 = 0
    for i in new_weight:
        norm2 += math.pow(new_weight[i], 2)
    norm2 = math.sqrt(norm2)
    if norm2 > (1/math.sqrt(lambd)):
        for i in new_weight: 
            G_WEIGHT[modelNum][i] = new_weight[i]/(norm2 * math.sqrt(lambd)) 
    else:
        G_WEIGHT[modelNum] = new_weight

def train_one_sample(data, num, sampleNum):
    for modelNum in range(10):
        if num == modelNum:
            label = 1
        else:
            label = -1
        train_one_model(data, label, sampleNum, modelNum)

if __name__== "__main__":
    for i in range(10):
        G_WEIGHT.append([])
        for j in range(32 * 32):
            G_WEIGHT[i].append(0)

    dirpath = "./trainingDigits/"
    files = os.listdir(dirpath)
    sampleNum = 0
    for file in files:
        print "training:", file
        data = parse_image(dirpath + file)
        num = int(file[0])
        sampleNum += 1
        train_one_sample(data, num, sampleNum)

    # test
    testdir = "./testDigits/"
    files = os.listdir(testdir)  
    for file in files:
        data = parse_image(testdir + file)
        print "testing:", file
        for i in range(10):
            pvalue = predict(G_WEIGHT[i], data)
            if pvalue > 0:
                print i, "prdict:", 1
            else:
                print i, "prdict:", -1
        
        
