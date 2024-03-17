from Crypto.Hash import keccak


def get_function_signature(function_abi: dict) -> str:
    input_types = ",".join([i["type"] for i in function_abi["inputs"]])
    input_signature = f"{function_abi['name']}({input_types})"
    return input_signature

def get_function_hash(function_abi: dict) -> str:
    input_signature = get_function_signature(function_abi)
    k = keccak.new(digest_bits=256)
    k.update(input_signature.encode('utf-8'))
    keccak_hash = k.hexdigest()
    return keccak_hash
