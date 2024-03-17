from multiprocessing import Process, Lock, Value
import ctypes
import random
from static_analyzer import annotate_contract
import json


def worker(storage_slot, lock):
    with lock:
        # Randomly set the storage slot to True or False
        storage_slot.value = random.choice([1, 0])

if __name__ == "__main__":
    n_addr = 10
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

    # Create a dictionary of booleans which indicate
    # if a storage slot is being used by another thread
    storage_accessed_by_another_thread = {
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

    # Launch worker processes to randomly set storage slots to True or False
    for contract_addr, attrs in storage_accessed_by_another_thread.items():
        for attr_name, slots in attrs.items():
            for i in range(len(slots)):
                p = Process(target=worker, args=(slots[i], storage_locks[contract_addr][attr_name][i]))
                p.start()
                p.join()

