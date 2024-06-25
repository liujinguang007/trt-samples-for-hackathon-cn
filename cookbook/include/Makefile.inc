CUDA_PATH       = /usr/local/cuda-11.4
NVCC            = $(CUDA_PATH)/bin/nvcc
TRT_INC_PATH    = /export/expand/liujinguang3/TensorRT-8.5.3.1/include
TRT_LIB_PATH    = /export/expand/liujinguang3/TensorRT-8.5.3.1/lib
#TRT_INC_PATH    = /export/expand/liujinguang3/TensorRT-8.6.1.6.1/include
#TRT_LIB_PATH    = /export/expand/liujinguang3/TensorRT-8.6.1.6/lib
GENCODE         = -gencode=arch=compute_86,code=sm_86
# -gencode=arch=compute_61,code=sm_61 -gencode=arch=compute_70,code=sm_70 -gencode=arch=compute_75,code=sm_75 -gencode=arch=compute_80,code=sm_80 -gencode=arch=compute_86,code=sm_86 -gencode=arch=compute_89,code=sm_89
DEBUG_MACRO     = -UDEBUG
WARNING_MACRO   = -w
CUFLAG          = -std=c++14 -O3 $(DEBUG_MACRO) -Xcompiler -fPIC $(GENCODE)
CCFLAG          = -std=c++14 -O3 $(DEBUG_MACRO) -Xcompiler -fPIC -use_fast_math
SOFLAG          = -shared
INCLUDE         = -I. -I$(CUDA_PATH)/include -I$(TRT_INC_PATH)
INCLUDE        += -I../../include -I../../../include
LDFLAG          = -L$(CUDA_PATH)/lib64 -lcudart -L$(TRT_LIB_PATH) -lnvinfer



