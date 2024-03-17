import random
import pprint
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor
from static_analyzer import annotate_contract
from multiprocessing import Value, Array, Process, Lock, Manager
import ctypes
from utils.filter import filter_parallelizable
from parallel_evmone import execute_mempool_parallel, run_evmone

import time

BLOCK_SIZE = 10


def worker_task(args, m, mutex_addresses, success_count, locks):

    # Assumption: Mutex BF goes up to 2D
    i, *rest = mutex_addresses + [None] * (3 - len(mutex_addresses))
    j = rest[0] if rest else 0
    k = rest[1] if rest else 0

    # TODO: Fix this naive implementation
    for bf, attr_dim in args:
        if attr_dim==1:
            locks[i] = 1

    # Handle case where mutex is locked
    if any(bf[i*m + j] for bf, attr_dim in args):
        print(f"Boolean at [{i},{j}] is Already in use")
        return False
    else:
        print(f"Boolean at [{i},{j}] is Free")
        success_count.value += 1





def run_superparallel(benchmark=False):


    addresses = list(range(10))

    contracts = {
        "X": {},
        "Y": {},
        "Z": {},
    }

    function_selectors = {}


    for contract_name in contracts.keys():
        annotate_contract(contract_name, "ERC20Basic")

    for contract_name, contract_details in contracts.items():
        abi_file_path = f"compiled_contracts/{contract_name}.abi.json"
        with open(abi_file_path, 'r', encoding='utf-8') as abi_file:
            abi_data = json.load(abi_file)
            for element in abi_data:
                if "dep_state_attr" in element:
                    contract_details[element["name"]] = element["dep_state_attr"]
                    function_selectors[element["name"]] = element["inputs"]

    # Extract the dep_state_attr for the contracts
    for contract_addr, write_func_deps in contracts.items():
        state_dep_attrs = {}
        # e.g. write_func_deps = {
        # 'approve': {'_allowances': 2},
        # 'transfer': {'_balances': 1},
        # 'transferFrom': {'_allowances': 2, '_balances': 1}
        # }
        for f_name, dep_states in write_func_deps.items():
            for attr in dep_states.keys():
                state_dep_attrs[attr] = dep_states[attr]
        contracts[contract_addr] = (state_dep_attrs, write_func_deps)



    print("Contracts")
    pprint.pprint(contracts)
    print("Function Selectors")
    pprint.pprint(function_selectors)

    n_addr = len(addresses)

    bloom_filters = {
        contract_addr: {
            attr_name: Array(
                    ctypes.c_bool,
                    n_addr**attr_dim
                )
            for attr_name, attr_dim in state_dep_attrs.items()
        }
        for contract_addr, (state_dep_attrs, write_func_deps) in contracts.items()
    }


    pprint.pprint(bloom_filters)

    result_flag = Value(ctypes.c_bool, False)
    success_count = Value('i', 0)  # 'i' is the type code for integers

    # Experiment
    mempool = [
        {
            "to": random.choice(list(contracts.keys())),
            "from": random.choice(addresses),
            "data": "",
            "f_name": random.choice(list(function_selectors.keys())),
            "involved_addresses": []
        }
        for _ in range(round(len(addresses) * len(contracts) * 0.8))
    ]

    # Decorate function_selectors
    # Assumption: Only address or uint types below 1024
    for tx in mempool:
        # e.g. f_input_abi = [
        #   {'internalType': 'address', 'name': 'spender', 'type': 'address'},
        #   {'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'}
        # ]
        f_input_abi = function_selectors[tx["f_name"]]
        for input_metadata_dict in f_input_abi:
            if input_metadata_dict["type"] == "address":
                input_metadata_dict["value"] = random.choice(addresses)
                tx["involved_addresses"] = list(
                    set(tx["involved_addresses"])
                    | {input_metadata_dict["value"]}
                )
            else:
                input_metadata_dict["value"] = random.choice(range(1024))



    # Step 1: Run mempool through bloom filters
    manager = Manager()

    # TODO Fix
    # num_locks = len(contracts)
    # locks = manager.list([Lock() for _ in range(num_locks)])
    # workers = []
    # Create a worker for each transaction in the mempool
    # Guaranteed to work due to parallelization
    # Some workers will be rejected due to mutex, but thats ok
    n_workers = len(mempool)

    for i in range(n_workers):
        # Worker i processes mempool[i]
        tx = mempool[i]
        contract_addr = tx["to"]
        f_name = tx["f_name"]
        contract_bf = bloom_filters[contract_addr]

        min_dim = float('inf')

        # e.g. affected_attrs_dict =  {'_allowances': 2}
        affected_attrs_dict = contracts[contract_addr][1][f_name]
        args = []
        for attr_name, attr_dim in affected_attrs_dict.items():
            args.append(
                (contract_bf[attr_name], attr_dim)
            )
            min_dim = min(min_dim, attr_dim)

        # TODO: Fix so it is a bit more nuanced than this. Need to modify annotate.py
        mutex_addresses = [tx["from"]] + tx["involved_addresses"]

        # worker_args = (args, n_addr, mutex_addresses, success_count, locks)
        # worker = Process(target=worker_task, args=worker_args)
        # workers.append(worker)
        # worker.start()
    
    mempool = filter_parallelizable(mempool, bloom_filters)



    # Step 2: Execute in Parallel in EVM
    start_time = time.time()
    execute_mempool_parallel(mempool)
    end_time = time.time()
    print(f"Execution time: {end_time - start_time} seconds")


    # TODO: Hook up to evm_tracer


    # Step 3: Run Sequencer on Return
    block_sequence = []

    # Step 4: Make State Update
    ##########################################
    #  DATABASE STATE UPDATES GO HERE
    #  Best to use concurrent data structures
    ##########################################

    # Step 5: Release all mutex








if __name__ == "__main__":
    run_superparallel()

