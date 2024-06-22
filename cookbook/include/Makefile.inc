CUDA_PATH       = /usr/local/cuda-11.4
NVCC            = $(CUDA_PATH)/bin/nvcc
TRT_INC_PATH    = /export/expand/liujinguang3/TensorRT-10.1.0.27/include
TRT_LIB_PATH    = /export/expand/liujinguang3/TensorRT-10.1.0.27/lib
#GENCODE         = -gencode=arch=compute_60,code=sm_60 -gencode=arch=compute_61,code=sm_61 -gencode=arch=compute_70,code=sm_70 -gencode=arch=compute_75,code=sm_75 -gencode=arch=compute_80,code=sm_80 -gencode=arch=compute_86,code=sm_86 -gencode=arch=compute_89,code=sm_89
GENCODE         = -gencode=arch=compute_86,code=sm_86
DEBUG_MACRO     = -UDEBUG
WARNING_MACRO   = -w
CUFLAG          = -std=c++17 -O3 $(DEBUG_MACRO) -Xcompiler -fPIC $(GENCODE)
CCFLAG          = -std=c++17 -O3 $(DEBUG_MACRO) -Xcompiler -fPIC -use_fast_math
SOFLAG          = -shared
INCLUDE         = -I. -I$(CUDA_PATH)/include -I$(TRT_INC_PATH)
INCLUDE        += -I$(TRT_COOKBOOK_PATH)/include
#LDFLAG          = -L$(CUDA_PATH)/lib64 -lcudart -L$(TRT_LIB_PATH) -lnvinfer -L$(TRT_COOKBOOK_PATH)/include -lz
LDFLAG          = -L$(CUDA_PATH)/lib64 -lcudart -L$(TRT_LIB_PATH) -lnvinfer -L$(TRT_COOKBOOK_PATH)/include -lz -ltrtutil


