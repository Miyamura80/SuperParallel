import utils as U
import re
import json
import subprocess
import pprint
from typing import List
import os

def annotate_contract(
    contract_identifier: str,
    contract_name: str,
    path: str = "contracts/reduced_erc20.sol",
) -> dict:
    """
    Analyzes a Solidity contract specified by its path, extracts relevant information,
    and generates a configuration JSON file. This file is saved with the name
    compiled_contracts/{contract_identifier}_config.json, containing the analysis results.

    Args:
        contract_identifier (str): Unique identifier for the contract.
        contract_name (str): The name of the contract.
        path (str): The file path to the Solidity contract. Defaults to "contracts/reduced_erc20.sol".
    """
    with open(path, "r", encoding="utf-8") as file:
        code = file.read()

    # Step 1: Compile the code. Reject if bytecode has DELEGATECALL

    # Compile the Solidity contract using solc
    compile_command = f"solc --optimize --combined-json abi,bin {path}"
    process = subprocess.Popen(
        compile_command, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise subprocess.CalledProcessError(
            process.returncode, compile_command, stderr.decode()
        )
    # Parse the output to JSON
    output = json.loads(stdout.decode())
    contract_data = output['contracts'][f"{path}:{contract_name}"]

    # Extract bytecode and ABI
    bytecode = contract_data['bin']
    abi: List[dict] = contract_data['abi']


    # Step 2: Extract the attributes from the contract
    #         and label so we know if it is shared across threads
    contract_attribute_pattern = (
        r'(\s*(?:uint(?:256|8|16|32|64)?|string|address|bool|mapping\(.+\))'
        r'(?:\s+mapping\(.+\))?'
        r')\s+(private|public|internal|external)'
        r'(?:\s+(constant|immutable))?\s+(_\w+);'
    )
    lines = code.split("\n")
    attr_dimensions = {}
    for line in lines:
        match = re.match(contract_attribute_pattern, line)
        if match:
            var_name = match.group(4)
            var_type = match.group(1)
            _var_visibility = match.group(2)
            attr_dimensions[var_name] = var_type.count("mapping")



    # Step 3: Regex-match all functions in contract
    #         and identify contracts as parallelizable or not
    function_annotation = {}

    func_pattern = re.compile(
        r'\bfunction\s+([^\s(]+(?:_[^\s(]+)*)\s*\(([^)]*)\)\s*'
        r'((?:public|private|internal|external)\s+)*'
        r'((?:payable|view|pure)\s+)*'
        r'((?:virtual|override)\s*)*'
        r'(returns\s*\(\s*([^)]+)\s*\))?'
    )
    # Find all matches using finditer for match objects
    matches = list(func_pattern.finditer(code))

    if not matches:
        raise ValueError("No function definitions were found in the contract code.")

    # Iterate through the match objects to extract function details
    for match in matches:
        function_name = match.group(1)
        parameters = match.group(2)
        visibility = match.group(3).strip() if match.group(3) else "default"
        state_mutability = match.group(4).strip() if match.group(4) else "state-mutating"
        return_type = match.group(7).strip() if match.group(7) else "no return type"

        function_definition = U.extract_function_definition(
            code, function_name
        )
        function_annotation[function_name] = {
            "name": function_name,
            "definition": function_definition,
            "parameters": parameters,
            "visibility": visibility,
            "stateMutability": state_mutability,
            "returnType": return_type,
        }


    # Define children node for each
    for f_name, f_annot in function_annotation.items():
        f_def_code = f_annot["definition"]
        potential_children = [
            name for name in function_annotation.keys() if name != f_name
        ]
        f_children = U.find_children(potential_children, f_def_code)
        function_annotation[f_name]["children"] = f_children

    # Recursively annotate the minimum dimension of mutex (mutex_dim)
    function_annotation = U.recursive_annotation(
        function_annotation, attr_dimensions
    )
    # (Visual Only) Cleanup
    for f_name in function_annotation.keys():
        if "definition" in function_annotation[f_name]:
            del function_annotation[f_name]["definition"]

    # Step 4: Generate the configuration JSON file & ABI

    compiled_contracts_dir = "compiled_contracts"
    os.makedirs(compiled_contracts_dir, exist_ok=True)

    # Modify ABI with `function_annotation`
    for f_name, f_annot in function_annotation.items():
        for f_abi in abi:
            if f_abi["type"]=="function" \
             and f_abi["name"] == f_name \
             and f_abi["stateMutability"] != "view":

                # Provide children + Mutex information
                f_abi["children"] = f_annot["children"]
                f_abi["mutex_dim"] = f_annot["mutex_dim"]
                f_abi["dep_state_attr"] = f_annot["dep_state_attr"]

                # Give the function signature
                f_abi["f_hash"] = U.get_function_hash(f_abi)


    # Save files
    abi_file_path = os.path.join(
        compiled_contracts_dir, f"{contract_identifier}.abi.json"
    )
    bytecode_file_path = os.path.join(
        compiled_contracts_dir, f"{contract_identifier}.bytecode.json"
    )

    with open(abi_file_path, 'w', encoding='utf-8') as abi_file:
        json.dump(abi, abi_file, indent=4)

    with open(bytecode_file_path, 'w', encoding='utf-8') as bytecode_file:
        json.dump({"bytecode": bytecode}, bytecode_file, indent=4)

    print(f"ABI and bytecode for {contract_identifier} have been saved to:")
    print(f"{abi_file_path}")
    print(f"{bytecode_file_path}")
    print("---")

if __name__ == "__main__":
    annotate_contract("X", "ERC20Basic")

