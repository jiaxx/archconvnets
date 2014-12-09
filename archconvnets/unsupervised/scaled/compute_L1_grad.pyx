cimport numpy as npd
import numpy as np

''' filters: in_channels, filter_sz, filter_sz, n_filters
    imgs: in_channels, img_sz, img_sz, n_imgs
'''
def L1_grad(npd.ndarray[npd.float64_t, ndim=4] F1, npd.ndarray[npd.float64_t, ndim=4] F2, npd.ndarray[npd.float64_t, ndim=4] F3, npd.ndarray[npd.float64_t, ndim=4] FL, npd.ndarray[npd.int_t, ndim=4] output_switches3_x, npd.ndarray[npd.int_t, ndim=4] output_switches3_y, npd.ndarray[npd.int_t, ndim=4] output_switches2_x, npd.ndarray[npd.int_t, ndim=4] output_switches2_y, npd.ndarray[npd.int_t, ndim=4] output_switches1_x, npd.ndarray[npd.int_t, ndim=4] output_switches1_y, int s1, int s2, int s3, npd.ndarray[npd.float64_t, ndim=2] pred, npd.ndarray[npd.float64_t, ndim=2] Y, npd.ndarray[npd.float64_t, ndim=4] imgs, npd.ndarray[npd.float64_t, ndim=5] sigma31, npd.ndarray[npd.int_t, ndim=1] img_cats): 
	cdef int N_C = FL.shape[0]
	cdef int cat
	cdef int N_IMGS = imgs.shape[3]
	cdef int max_output_sz3 = output_switches3_x.shape[1]
	cdef int n3 = output_switches3_x.shape[0]
	cdef int n2 = output_switches2_x.shape[0]
	cdef int n1 = output_switches1_x.shape[0]
	cdef int img
	cdef int channel_
	cdef int f1_
	cdef int a1_x_
	cdef int a1_y_
	cdef npd.ndarray[npd.float64_t, ndim=4] grad = np.zeros_like(F1)
	cdef int a3_y
	cdef int a3_x
	cdef int f3
	cdef int f2
	cdef int z1
	cdef int z2
	cdef int a2_x
	cdef int a2_y
	cdef int a3_x_global
	cdef int a3_y_global
	cdef int a2_x_global
	cdef int a2_y_global
	cdef int a1_x_global
	cdef int a1_y_global	
	cdef float temp_F_prod_all
	cdef float px
	cdef float F32
	cdef float FL32
	
	for a3_x in range(s3):
		for a3_y in range(s3):
			for f1_ in range(n1):
				for f3 in range(n3):
					for f2 in range(n2):
						for a2_x in range(s2):
							for a2_y in range(s2):
								F32 = F3[f3, f2, a3_x, a3_y] * F2[f2, f1_, a2_x, a2_y]
								for z1 in range(max_output_sz3):
									for z2 in range(max_output_sz3):
										for img in range(N_IMGS):
											FL32 = F32 * FL[img_cats[img], f3, z1, z2]
											for a1_x_ in range(s1):
												for a1_y_ in range(s1):
													for channel_ in range(3):
														# supervised term:
														grad[f1_, channel_, a1_x_, a1_y_] -= FL32 * sigma31[img_cats[img], channel_, f1_, a1_x_, a1_y_]
	return grad


