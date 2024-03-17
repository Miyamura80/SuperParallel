from static_analyzer import annotate_contract
import json
import random
import time
from parallel_evmone import run_evmone

def run_serial(benchmark=False):
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

    start_time = time.time()
    for i, tx in enumerate(mempool):
        run_evmone(
            tx["to"],
            tx["data"],
            f"{i}",
        )
    end_time = time.time()
    print(f"Execution time: {end_time - start_time} seconds")

if __name__ == "__main__":
    run_serial()
