#include "includes.h"

#define CHECK_CUDA_ERR {err = cudaGetLastError();if(err != cudaSuccess){\
		printf("CUDA error: %s, %s, %i\n",cudaGetErrorString(err),__FILE__,__LINE__);return NULL;}}

#define CHECK_CUDA_ERR_R {err = cudaGetLastError();if(err != cudaSuccess){\
		printf("CUDA error: %s, %s, %i\n",cudaGetErrorString(err),__FILE__,__LINE__);return;}}

#include "conv.c"
#include "conv_dfilter.c"
#include "conv_dfilter_stream.c"
#include "conv_ddata.c"
#include "init_buffers.c"
#include "set_img_buffer.c"
#include "set_filter_buffer.c"
#include "set_conv_buffer.c"
#include "conv_from_buffers.c"
#include "max_pool_locs_alt.c"
#include "pool_alt_inds_opt_patches.c"
#include "max_pool_cudnn.c"
#include "max_pool_back_cudnn.c"
#include "unpool.c"


static PyMethodDef _cudnn_module[] = {
	{"conv", conv, METH_VARARGS},
	{"conv_dfilter_stream", conv_dfilter_stream, METH_VARARGS},
	{"conv_dfilter", conv_dfilter, METH_VARARGS},
	{"conv_ddata", conv_ddata, METH_VARARGS},
	{"init_buffers", init_buffers, METH_VARARGS},
	{"set_img_buffer", set_img_buffer, METH_VARARGS},
	{"set_filter_buffer", set_filter_buffer, METH_VARARGS},
	{"set_conv_buffer", set_conv_buffer, METH_VARARGS},
	{"conv_from_buffers", conv_from_buffers, METH_VARARGS},
	{"max_pool_locs_alt", max_pool_locs_alt, METH_VARARGS},
	{"max_pool_locs_alt_patches", max_pool_locs_alt_patches, METH_VARARGS},
	{"max_pool_cudnn", max_pool_cudnn, METH_VARARGS},
	{"max_pool_back_cudnn", max_pool_back_cudnn, METH_VARARGS},
	{"unpool", unpool, METH_VARARGS},
	{NULL, NULL}
};

void init_cudnn_module(){
	(void) Py_InitModule("_cudnn_module", _cudnn_module);
	import_array();
	
	cudnnStatus_t status;
	status = cudnnCreate(&handle);  ERR_CHECK_R
	
	cudaError_t err;
	for(int gpu = 0; gpu < N_GPUS; gpu++){
		cudaSetDevice(gpu); CHECK_CUDA_ERR_R
		cudaStreamCreate(&streams[gpu]); CHECK_CUDA_ERR_R
	}
	
	//---------------------------------------
	// Create general Descriptors
	//---------------------------------------
	status = cudnnCreateTensor4dDescriptor(&srcDesc);  ERR_CHECK_R
	status = cudnnCreateTensor4dDescriptor(&gradDesc_data);  ERR_CHECK_R
	status = cudnnCreateTensor4dDescriptor(&destDesc);  ERR_CHECK_R
	status = cudnnCreateFilterDescriptor(&filterDesc);  ERR_CHECK_R
	status = cudnnCreateFilterDescriptor(&gradDesc_filter);  ERR_CHECK_R
	status = cudnnCreateConvolutionDescriptor(&convDesc);  ERR_CHECK_R
	
	status = cudnnCreatePoolingDescriptor(&poolingDesc);  ERR_CHECK_R
	status = cudnnCreateTensor4dDescriptor(&srcDiffDesc);  ERR_CHECK_R
	status = cudnnCreateTensor4dDescriptor(&destDiffDesc);  ERR_CHECK_R
	
	status = cudnnSetPoolingDescriptor(poolingDesc, CUDNN_POOLING_MAX, POOL_WINDOW_SZ, POOL_WINDOW_SZ, POOL_STRIDE, POOL_STRIDE); ERR_CHECK_R
	
	return;
} 
