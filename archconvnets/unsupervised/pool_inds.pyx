cimport numpy as npd
import numpy as np

''' conv_output: 
'''
def max_pool_locs(npd.ndarray[npd.float32_t, ndim=4] conv_output, int pool_stride=2, int pool_window_sz=3): 
	conv_output = conv_output.transpose((1,2,3,0)) # todo: change function to work with this dimension ordering natively
	assert conv_output.shape[1] == conv_output.shape[2]
	
	cdef int conv_sz = conv_output.shape[1]
	cdef int x_loc = 0
	cdef int y_loc = 0
	cdef int x = 0
	cdef int y = 0
	cdef int filter
	cdef int n_filters = conv_output.shape[0]
	cdef int n_imgs = conv_output.shape[3]
	cdef int output_sz = len(range(0,conv_sz-pool_window_sz,pool_stride))
	
	cdef npd.ndarray[npd.float32_t, ndim=4] output = np.zeros((n_filters, output_sz, output_sz, n_imgs), dtype='single')
	cdef npd.ndarray[npd.int_t, ndim=4] output_switches_x = np.zeros((n_filters, output_sz, output_sz, n_imgs),dtype='int')
	cdef npd.ndarray[npd.int_t, ndim=4] output_switches_y = np.zeros((n_filters, output_sz, output_sz, n_imgs),dtype='int')
	cdef npd.ndarray[npd.float32_t, ndim=3] output_patch
	cdef npd.ndarray[npd.float32_t, ndim=2] output_patch_flat
	cdef npd.ndarray[npd.int_t, ndim=1] inds

	for x_loc in range(0,conv_sz-pool_window_sz,pool_stride):
		y = 0
		for y_loc in range(0,conv_sz-pool_window_sz,pool_stride):
			for filter in range(n_filters):
				output_patch = conv_output[filter,x_loc:x_loc+pool_window_sz, y_loc:y_loc+pool_window_sz]
				output_patch_flat = output_patch.reshape((output_patch.shape[0]*output_patch.shape[1], n_imgs))

				inds = np.argmax(output_patch_flat,axis=0)
				global_inds = np.asarray(np.unravel_index(inds, (output_patch.shape[0],output_patch.shape[1]))) + np.array([x_loc, y_loc])[:,np.newaxis]
				output[filter,x,y] = output_patch_flat[inds, range(n_imgs)]
				output_switches_x[filter,x,y] = global_inds[0]
				output_switches_y[filter,x,y] = global_inds[1]

			y += 1
		x += 1
		
	## todo:
	output = np.ascontiguousarray(output.transpose((3,0,1,2)))
	output_switches_x = np.ascontiguousarray(output_switches_x.transpose((3,0,1,2)))
	output_switches_y = np.ascontiguousarray(output_switches_y.transpose((3,0,1,2)))
	return output, output_switches_x, output_switches_y

