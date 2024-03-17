import subprocess
from concurrent.futures import ThreadPoolExecutor
import json
import time

EXECUTION_LOG_DIR = "execution_logs"
PROGRAM_NAME = "evmone_parallel_evm"

def run_evmone(
    contract_name: str,
    call_data: str,
    run_hash: str,
    compile_dir: str="compiled_contracts",
) -> None:
    time.sleep(2)
    bytecode_file = f"{compile_dir}/{contract_name}.bytecode.json"
    with open(bytecode_file, 'r', encoding='utf-8') as file:
        bytecode_json = file.read()
    bytecode_data = json.loads(bytecode_json)
    bytecode = bytecode_data["bytecode"]

    command = (
        f"./build/{PROGRAM_NAME} --bytecode {bytecode} "
        f"--tracefilename test_trace.json --calldata \"{call_data}\" "
        f"--outputdir={EXECUTION_LOG_DIR} --fileprefix={run_hash}_"
    )
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        print("Script executed successfully")
        print(stdout.decode())
    else:
        print("Error in script execution")
        print(stderr.decode())

def execute_mempool_parallel(mempool):
    # Number of times you want to run the script in parallel
    num_parallel_runs = len(mempool)

    # Using ThreadPoolExecutor to run the script in parallel
    with ThreadPoolExecutor(max_workers=num_parallel_runs) as executor:
        futures = [
            executor.submit(
                run_evmone,
                tx["to"],
                tx["data"],
                f"{i}")
            for i, tx in enumerate(mempool)
        ]
        for future in futures:
            future.result()  # Wait for all futures to complete


