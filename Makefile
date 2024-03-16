PROGRAM_NAME = evmone_parallel_evm
DEPS_PATH = ./deps/
EVMONE_PATH = ./deps/evmone
INCLUDES = -I$(EVMONE_PATH)/evmc/include -I$(EVMONE_PATH)/include -I$(EVMONE_PATH)/lib/evmone -I$(EVMONE_PATH)/lib -I$(DEPS_PATH)/intx/include
LIBRARIES = -L$(EVMONE_PATH)/build/evmc/lib/loader -L$(EVMONE_PATH)/build/lib

setup_evmone:
	# Step 1: Build the evmone repo
	# cd ./deps/evmone && cmake -S . -B build -DEVMONE_TESTING=ON && cmake --build build --parallel

	# Step 2: Build the evmone evm trace generation
	g++ -std=c++20 -o build/$(PROGRAM_NAME) evm_tracer.cpp $(INCLUDES) $(LIBRARIES) -levmc-loader -levmone -Wl,-rpath,$(realpath $(EVMONE_PATH)/build/lib)

	# ./utils/evm_runners/evmone/$(PROGRAM_NAME) --bytecode 604260005260206000F3 --tracefilename test_trace.json --calldata ""
