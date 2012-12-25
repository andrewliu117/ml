#!/usr/bin/env python
# -*- coding: utf-8 -*-

### ###
# 基于SVM的手写数字的识别程序
# 数据：采用了《Marchine Learning in Action》第二章的数据
### ###

import sys
import os
import math

class model:
    def __init__(self):
        self.a = []
        self.b = 0.0

class GV:
    def __init__(self):
        self.samples = []        # 样本数据
        self.tests = []          # 测试数据
        self.models = []         # 训练的模型
        self.diff_dict = []         # 用于缓存预测知与真实y之差Ei
        self.cur_mno = 0         # 当前正使用或训练的模型

    def init_models(self):
        for i in range(0, 10):
            m = model()
            for j in range(len(self.samples)):
                m.a.append(0)
            self.models.append(m)

class image:
    def __init__(self):
        self.data = []
        self.num = 0
        self.label = 0
        self.fn = ""

# global variables
gv = GV()

def parse_image(path):
    img_map = []
    fp = open(path, "r") 
    for line in fp:
        line = line[:-2]
        img_map.append(line)
    return img_map


# load samples and tests
def loaddata(dirpath, col):
    files = os.listdir(dirpath)
    for file in files:
        img = image()
        img.data = parse_image(dirpath + file)
        img.num = int(file[0])
        img.fn = file
        col.append(img)

######
# 高斯核函数
######
def kernel(mj, mi):
    if mj == mi:
        return math.exp(0)
    dlt = 100
    ret = 0.0
    for i in range(len(mj.data)):
        ret += math.pow(int(mj.data[i]) - int(mi.data[i]), 2)
    ret = math.exp(-ret/(2*dlt*dlt))
    return ret

# g(x)
def predict(m):
    pred = 0.0
    for j in range(len(gv.samples)):
        if gv.models[gv.cur_mno].a[j] != 0:
            pred += gv.models[gv.cur_mno].a[j] * gv.samples[j].label * kernel(gv.samples[j],m)
    pred += gv.models[gv.cur_mno].b 
    return pred

# 决策函数对xi的预测值和真实值之差
def predict_diff_real(i):
    diff = predict(gv.samples[i])
    diff -= gv.samples[i].label
    return diff


def init_predict_diff_real_dict():
    for i in range(len(gv.samples)):
        gv.diff_dict.append(predict_diff_real(i))

def update_diff_dict():
    for i in range(len(gv.samples)):
        gv.diff_dict[i] = predict_diff_real(i)

def update_samples_label(num):
    for img in gv.samples:
        if img.num == num:
            img.label = 1
        else:
            img.label = -1

######
#  svmocr train
#  基于算法SMO
#  T: tolerance 误差容忍度(精度)
#  times: 迭代次数
#  C: 惩罚系数
#  Mno: 模型序号0到9
######
def SVM_SMO_train(T, times, C, Mno):
    time = 0
    gv.cur_mno = Mno
    update_samples_label(Mno)
    init_predict_diff_real_dict()
    updated = True
    while time < times and updated:
        updated = False
        time += 1
        for i in range(len(gv.samples)):
            ai = gv.models[gv.cur_mno].a[i]
            Ei = gv.diff_dict[i]

            # agaist the KKT
            if (gv.samples[i].label * Ei < -T and ai < C) or (gv.samples[i].label * Ei > T and ai > 0):
                for j in range(len(gv.samples)):
                    if j == i: continue
                    kii = kernel(gv.samples[i],gv.samples[i])
                    kjj = kernel(gv.samples[j],gv.samples[j])
                    kji = kij = kernel(gv.samples[i],gv.samples[j])
                    eta = kii + kjj - 2 * kij 
                    if eta <= 0: continue
                    new_aj = gv.models[gv.cur_mno].a[j] + gv.samples[j].label * (gv.diff_dict[i] - gv.diff_dict[j]) / eta # f 7.106
                    L = 0.0
                    H = 0.0
                    a1_old = gv.models[gv.cur_mno].a[i]
                    a2_old = gv.models[gv.cur_mno].a[j]
                    if gv.samples[i].label == gv.samples[j].label:
                        L = max(0, a2_old + a1_old - C)
                        H = min(C, a2_old + a1_old)
                    else:
                        L = max(0, a2_old - a1_old)
                        H = min(C, C + a2_old - a1_old)
                    if new_aj > H:
                        new_aj = H
                    if new_aj < L:
                        new_aj = L
                    if abs(a2_old - new_aj) < 0.0001:
                        print "j = %d, is not moving enough" % j
                        continue

                    new_ai = a1_old + gv.samples[i].label * gv.samples[j].label * (a2_old - new_aj) # f 7.109 
                    new_b1 = gv.models[gv.cur_mno].b - gv.diff_dict[i] - gv.samples[i].label * kii * (new_ai - a1_old) - gv.samples[j].label * kji * (new_aj - a2_old) # f7.115
                    new_b2 = gv.models[gv.cur_mno].b - gv.diff_dict[j] - gv.samples[i].label*kji*(new_ai - a1_old) - gv.samples[j].label*kjj*(new_aj-a2_old)    # f7.116
                    if new_ai > 0 and new_ai < C: new_b = new_b1
                    elif new_aj > 0 and new_aj < C: new_b = new_b2
                    else: new_b = (new_b1 + new_b2) / 2.0

                    gv.models[gv.cur_mno].a[i] = new_ai
                    gv.models[gv.cur_mno].a[j] = new_aj
                    gv.models[gv.cur_mno].b = new_b
                    update_diff_dict()
                    updated = True
                    print "iterate: %d, changepair: i: %d, j:%d" %(time, i, j)
                    break


# 测试数据
def test():
    for img in gv.tests: 
        for mno in range(10):
            gv.cur_mno = mno
            if predict(img) > 0:
                img.label = mno
                print mno
                print img.fn
                sys.exit(0)

    

if __name__ == "__main__":
    loaddata("trainingDigits/", gv.samples)
    loaddata("testDigits/", gv.tests)    
    print len(gv.samples)
    print len(gv.tests)

    gv.init_models()

    T = 0.01
    C = 5
    for i in range(10):
        SVM_SMO_train(T, 100, C, i)

    test()
