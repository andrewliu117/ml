#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import sys 

def load_data(fname):
	f = open(fname)
	y=[]
	x=[]
	for line in f:
		line=line.strip('\n')
		str_list=line.split(' ')
		xi=[]
		for v in str_list:
			if v[0] == 'c':
				yi=v[-1:]
				y.append(int(yi))
			if v[0] == 'f':
				xij=v[-1:]
				xi.append(int(xij))
		x.append(xi)
	f.close()
	y_max=1
	for yval in y:
		if yval > y_max:
			y_max=yval
	x_max=[]
	for xval in x[0]:
		x_max.append(xval)
	for xvec in x:
		for i in range(len(xvec)):
			if xvec[i] > x_max[i]:
				x_max[i] = xvec[i]
	print x_max
	print y_max
	return x,y,x_max,y_max

class FeatureParam:
	def __init__(self,ft_index,except_class,except_ft_val):
		self.w=0.0
		self.ft_index=ft_index
		self.except_class=except_class
		self.except_ft_val=except_ft_val
	def feature_func(self,xvec,y):
		if y == self.except_class and xvec[self.ft_index] == self.except_ft_val:
			return 1
		else:
			return 0

def init_feature_func_and_param(x_max_vec,y_max):
	fvec=[]
	ft_index=-1
	print "x_max,", x_max_vec
	print "y_max,", y_max
	for x_max in x_max_vec:
		ft_index+=1
		for xval in range(0,x_max+1):
			for yval in range(1,y_max+1):
				fp=FeatureParam(ft_index,yval,xval)
				fvec.append(fp)
	return fvec

def estimated_except_feature_val(x_mat,y_vec,fparam):
	esti_efi = 0.0
	n_data=len(y_vec)
	for i in range(n_data):
		x_vec = x_mat[i]
		esti_efi += fparam.feature_func(x_vec,y_vec[i])
	# perhaps there's no data match the feature function
	# to make the computation possible, let it be a small float number
	if esti_efi == 0.0:
		esti_efi = 0.0000001
	esti_efi /= 1.0*n_data
	return esti_efi

def max_ent_predict_unnormalized(x_vec,y,fvec):
	weighted_sum=0.0
	for fparam in fvec:
		weighted_sum += fparam.w * fparam.feature_func(x_vec,y)
	return math.exp(weighted_sum)

def max_ent_normalizer(x_vec,y_max,fvec):
	zw=0.0
	for y in range(1,y_max+1):
		zw += max_ent_predict_unnormalized(x_vec,y,fvec)
	return zw

def model_except_feature_val(x_mat,y_max,fparam,fvec,p_cached):
	data_size=len(x_mat)
	efi=0.0
	index=0
	ix=-1
	for x_vec in x_mat:
		ix += 1
		zw=0.0
		tmp_efi=0.0
		for y in range(1,y_max+1):
			# compute p(y|x) at current w
			# in same iteration, p(y|x) not change, so can cache it
			if index < len(p_cached):
				p_y_given_x = p_cached[index]
			else:
				p_y_given_x = max_ent_predict_unnormalized(x_vec,y,fvec)
				p_cached.append(p_y_given_x)
			zw += p_y_given_x
			tmp_efi += p_y_given_x * fparam.feature_func(x_vec,y)
			index+=1
		tmp_efi /= zw
		efi += tmp_efi
	efi /= data_size
	if efi == 0.0:
		efi = 0.0000001
	return efi

def feature_func_sum(fvec,xvec,y):
	m = 0.0
	for f in fvec:
		m += f.feature_func(xvec,y)
	return m

def update_param(x_mat,y_vec,y_max,fvec):
	m = feature_func_sum(fvec,x_mat[0],y_vec[0])
	convergenced = True
	sigma_sqr_sum=0.0
	w_updated=[]
	p_cached=[]
	for fparam in fvec:
		esti_efi = estimated_except_feature_val(x_mat,y_vec,fparam)
		efi = model_except_feature_val(x_mat,y_max,fparam,fvec,p_cached)
		sigma_i= math.log(esti_efi/efi) / m
		w_updated.append(fparam.w + sigma_i)
		if abs(sigma_i/(fparam.w+0.000001)) >= 0.10:
			convergenced = False
		sigma_sqr_sum += sigma_i*sigma_i
	i=0
	for fparam in fvec:
		fparam.w = w_updated[i]
		i+=1
	print("sigma_len=%f"%math.sqrt(sigma_sqr_sum))
	return convergenced

def log_likelihood(x_mat,y_vec,y_max,fvec):
	ix=-1
	log_likelihood = 0.0
	data_size = len(x_mat)
	for i in range(data_size):
		x_vec = x_mat[i]
		y = y_vec[i]
		log_likelihood += math.log(max_ent_predict_unnormalized(x_vec,y,fvec))
		log_likelihood -= math.log(max_ent_normalizer(x_vec,y_max,fvec))
	log_likelihood /= data_size
	return log_likelihood

def max_ent_train(x_mat,y_vec,x_max_vec,y_max):
	fvec = init_feature_func_and_param(x_max_vec,y_max)
	iter_time=0
	while True:
		convergenced=update_param(x_mat,y_vec,y_max,fvec)
		log_lik=log_likelihood(x_mat,y_vec,y_max,fvec)
		print("log_likelihood=%0.12f"%log_lik)
		if convergenced:
			break
		iter_time+=1
		if iter_time >= 100:
			break
	fmodel=open('./model.txt','w')
	for fparam in fvec:
		fmodel.write(str(fparam.w))
		fmodel.write('\n')
	fmodel.close()
	print("max ent train ok!")

def load_model():
	x_mat,y_vec,x_max_vec,y_max=load_data("zoo.train")
	fvec = init_feature_func_and_param(x_max_vec,y_max)
	fmod=open('./model.txt')
	i=-1
	for line in fmod:
		i+=1
		line=line.strip('\n')
		fvec[i].w=float(line)
	fmod.close()
	return fvec,y_max

def max_ent_test():
	fvec,y_max = load_model()
	x_mat_test,y_vec_test,x_max_vec_test,y_max_test=load_data("zoo.test")
	test_size=len(x_mat_test)
	ok_num=0
	for i in range(test_size):
		x_vec=x_mat_test[i]
		y=y_vec_test[i]
		most_possible_predict_y=0
		max_p=0.0
		for predict_y in range(1,y_max+1):
			p = max_ent_predict_unnormalized(x_vec,predict_y,fvec)
			if p > max_p:
				most_possible_predict_y = predict_y
				max_p = p
		if y == most_possible_predict_y:
			ok_num += 1
		print("y=%d predict_y=%d"%(y,most_possible_predict_y))
	print("precision-ratio=%f"%(1.0*ok_num/test_size))

if __name__=="__main__":
	if len(sys.argv) == 1:
		argv = "train"
	else:
		argv = sys.argv[1]
	if argv == 'train':
		x_mat,y_vec,x_max_vec,y_max=load_data("zoo.train")
		max_ent_train(x_mat,y_vec,x_max_vec,y_max)
	if argv == 'test':
		max_ent_test()
