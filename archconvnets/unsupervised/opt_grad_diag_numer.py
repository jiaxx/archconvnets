from scipy.spatial.distance import squareform
import copy
import time
from scipy.stats import pearsonr
import scipy.optimize
import numpy as np
import random
from scipy.spatial.distance import pdist
from scipy.io import loadmat
from scipy.io import savemat
from scipy.stats.mstats import zscore
#from archconvnets.unsupervised.opt_grad_third_order_reduced_second_order import test_grad
import math

global filename
if False:
	n_channels_in = 64
	filter_sz = 5

	n_channels_out = 64
	n_channels_find = 64

	filters_name = 'filters_layer2_4layermodel'
else:
	n_channels_in = 3
	filter_sz = 5
	
	n_channels_out = 64
	n_channels_find = 64
	
	filters_name = 'filters_layer1_4layermodel'

def test_grad(x):
	N = n_channels_find
	x_in = copy.deepcopy(x)
	x = copy.deepcopy(x_g) #x.reshape((in_dims,N))
	x[10,4] = x_in
	x_mean = np.mean(x,axis=1)
	x_no_mean = x - x_mean[:,np.newaxis]
	x_no_mean2 = x_no_mean ** 2

	diag_mat = np.zeros((in_dims, in_dims))
	for i in range(in_dims):
          for j in range(in_dims):
                  if i != j:
                          diag_mat[i,j] = np.sum(x_no_mean2[i]*x_no_mean[j])
	loss = np.sum(np.abs(target_diag_mat - diag_mat))
	return loss

def test_grad_grad(x):
        N = n_channels_find
        x_in = copy.deepcopy(x)
        x = copy.deepcopy(x_g) #x.reshape((in_dims,N))
        x[10,4] = x_in
	x_mean = np.mean(x,axis=1)
        x_no_mean = x - x_mean[:,np.newaxis]
        x_no_mean2 = x_no_mean ** 2
	
	diag_mat = np.zeros((in_dims, in_dims))
        for i in range(in_dims):
          for j in range(in_dims):
                  if i != j:
                          diag_mat[i,j] = np.sum(x_no_mean2[i]*x_no_mean[j])
	sign_mat = 1 - 2*(diag_mat < target_diag_mat)
	grad = np.zeros((in_dims,N))
	r = 10

        ################# r < m
	for m in range(in_dims):
                if r != m:
                        t = x_no_mean[r]*x_no_mean[m]
                        grad[r] += sign_mat[r,m]*(2.0*(t - (1.0/N)*np.sum(t)))
                        grad[r] += sign_mat[m,r]*(x_no_mean2[m] - (1.0/N)*np.sum(x_no_mean2[m]))
	return grad[10,4] #grad.reshape((1,in_dims*N)).T

in_dims = n_channels_in*(filter_sz**2)
#################
N = n_channels_find
filename = 'opt_' + filters_name + '_thirdorder_grad_diag_numer.mat'

filters = loadmat(filters_name + '.mat')['filters']
in_dims = n_channels_in*(filter_sz**2)
filters = filters.reshape((in_dims, n_channels_out))

x_g = np.random.random((in_dims, N))

#################
# compute target third order diags
#x_no_mean = 
x = copy.deepcopy(filters) #t = zscore(filters)

x_mean = np.mean(x,axis=1)
x_no_mean = x - x_mean[:,np.newaxis]
x_no_mean2 = x_no_mean ** 2

target_diag_mat = np.zeros((in_dims, in_dims))
for i in range(in_dims):
	for j in range(in_dims):
		if i != j:
			target_diag_mat[i,j] = np.sum(x_no_mean2[i]*x_no_mean[j])
		
x0 = np.random.random((1,1)) #x0.reshape((in_dims*N, 1))
t_start = time.time()
time_save = time.time()
print filename
#print test_grad(x0, target, filename, inds_flat_eval)[0]#, target, filename)[0]
print 'starting...'
print scipy.optimize.check_grad(test_grad, test_grad_grad, x0.T)
#x, f, d = scipy.optimize.fmin_l_bfgs_b(test_grad, x0.reshape(in_dims*N,1))
print time.time() - t_start

