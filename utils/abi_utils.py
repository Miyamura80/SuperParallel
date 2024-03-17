from Crypto.Hash import keccak


def get_function_signature(function_abi: dict) -> str:
    """
    Generates the function signature from the ABI (Application Binary Interface) definition.

    Args:
        function_abi (dict): The ABI definition of the function, containing its name and inputs.

    Returns:
        str: The function signature as a string, which includes the function name and comma-separated list of input types.
    """
    input_types = ",".join([i["type"] for i in function_abi["inputs"]])
    input_signature = f"{function_abi['name']}({input_types})"
    return input_signature

def get_function_hash(function_abi: dict) -> str:
    """
    Computes the Keccak-256 hash of the function signature derived from its ABI definition and returns the first 4 bytes.

    This hash is often used to uniquely identify functions within the Ethereum ecosystem.

    Args:
        function_abi (dict): The ABI definition of the function, containing its name and inputs.

    Returns:
        str: The first 8 characters of the Keccak-256 hash of the function signature, representing the first 4 bytes.
    """
    input_signature = get_function_signature(function_abi)
    k = keccak.new(digest_bits=256)
    k.update(input_signature.encode('utf-8'))
    keccak_hash = k.hexdigest()
    # Take the first 4 bytes of the keccak_hash
    return keccak_hash[:8]
