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
import itertools
import time

BLOCK_SIZE = 10
N_ADDRESSES = 10


def worker_task(
    args, m, tx_id, mutex_addresses, success_count
):

    counter = 0
    # BACKLOG: Fix this naive implementation
    for bf, attr_dim, locks_for_workers in args:
        for perm in itertools.permutations(mutex_addresses, attr_dim):
            with locks_for_workers[counter]:
                index = sum([x*m**i for i, x in enumerate(perm)])
                bf[index].value = 1
                counter += 1





    # # Handle case where mutex is locked
    # if any(bf[i*m + j] for bf, attr_dim in args):
    #     print(f"Boolean at [{i},{j}] is Already in use")
    #     return False
    # else:
    #     print(f"Boolean at [{i},{j}] is Free")
    #     success_count.value += 1





def run_superparallel(benchmark=False):



    addresses = list(range(1,N_ADDRESSES+1))

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
            attr_name: [
                    Value(ctypes.c_bool, False)
                    for _ in range(n_addr**attr_dim)
                ]
            for attr_name, attr_dim in state_dep_attrs.items()
        }
        for contract_addr, (state_dep_attrs, write_func_deps) in contracts.items()
    }

    storage_locks = {
        contract_addr: {
            attr_name: [
                Lock() for _ in range(n_addr**attr_dim)
            ]
            for attr_name, attr_dim in state_dep_attrs.items()
        }
        for contract_addr, (state_dep_attrs, write_func_deps) in contracts.items()
    }


    success_count = Value('i', 0)  # 'i' is the type code for integers

    # Demo Purposes
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
    workers = []
    # Create a worker for each transaction in the mempool
    # Guaranteed to work due to parallelization
    # Some workers will be rejected due to mutex, but thats ok

    for tx_id, tx in enumerate(mempool):
        # Worker i processes mempool[i]
        contract_addr = tx["to"]
        f_name = tx["f_name"]
        # TODO: Fix so it is a bit more nuanced than this. Need to modify annotate.py
        mutex_addresses = [tx["from"]] + tx["involved_addresses"]

        contract_bf = bloom_filters[contract_addr]
        contract_owned_locks = storage_locks[contract_addr]


        # e.g. affected_attrs_dict =  {'_allowances': 2}
        affected_attrs_dict = contracts[contract_addr][1][f_name]
        args = []
        for attr_name, attr_dim in affected_attrs_dict.items():

            locks_for_workers = []
            for perm in itertools.permutations(mutex_addresses, attr_dim):
                index = sum([x*n_addr**i for i, x in enumerate(perm)])
                locks_for_workers.append(
                    contract_owned_locks[attr_name][index]
                )

            # Add final args to pass to the worker
            args.append(
                (contract_bf[attr_name], attr_dim, locks_for_workers)
            )

        worker_args = (args, n_addr, tx_id, mutex_addresses, success_count)
        worker = Process(target=worker_task, args=worker_args)
        workers.append(worker)
        worker.start()

    mempool = filter_parallelizable(mempool, bloom_filters)



    # Step 2: Execute in Parallel in EVM
    # start_time = time.time()
    # execute_mempool_parallel(mempool)
    # end_time = time.time()
    # print(f"Execution time: {end_time - start_time} seconds")







if __name__ == "__main__":
    run_superparallel()

