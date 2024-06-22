include $(TRT_COOKBOOK_PATH)/include/Makefile.inc

SOURCE_CPP  = $(shell find . -name '*.cpp' 2>/dev/null)
OBJ         = $(shell find . -name *.o 2>/dev/null)
DEP         = $(OBJ:.o=.d)
# TARGET_EXE  = $(SOURCE_CPP:.cpp=.o)
TARGET_LIB := libtrtutil.so

-include $(DEP)

all: $(TARGET_LIB)

$(TARGET_LIB): cookbookHelper.o cnpy.o calibrator.o
	$(NVCC) $(CCFLAG) $(LDFLAG) -shared -o $@ $^

# %.o: %.cpp
# 	$(NVCC) $(CCFLAG) $(INCLUDE) -M -MT $@ -o $(@:.o=.d) $<
# 	$(NVCC) $(CCFLAG) $(INCLUDE) -Xcompiler -fPIC -o $@ -c $<
cookbookHelper.o:cookbookHelper.cu
	$(NVCC) $(CCFLAG) $(INCLUDE) -Xcompiler -fPIC -c -o $@ $^

cnpy.o:cnpy.cpp
	$(NVCC) $(CCFLAG) $(INCLUDE) -Xcompiler -fPIC -c -o $@ $^

calibrator.o:calibrator.cpp
	$(NVCC) $(CCFLAG) $(INCLUDE) -Xcompiler -fPIC -c -o $@ $^

.PHONY: build
build:
	make clean
	make

.PHONY: clean
clean:
	rm -rf *.d *.o *.so *.exe *.trt
