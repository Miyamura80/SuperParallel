"""
Solidity file utils.
"""
import re

def hello_world():
    print("Helo world")
    return ""


def transform_contract_public(code):
    contract_name = extract_contract_name(code)

    lines = code.split("\n")
    public_pattern = (
        r"\b(address|uint256|uint8|bool|string|bytes32|"
        r"mapping\(.+ => .+\))\s+(public\s+|private\s+|internal\s+)?(\w+)\s*;"
    )
    for i, line in enumerate(lines):
        match = re.search(public_pattern, line)
        if match:
            lines[i] = line.replace(
                match.group(0), f"{match.group(1)} public {match.group(3)};"
            )

    for i, line in enumerate(lines):
        if contract_name in line:
            lines[i] = line.replace(contract_name, "TargetContract")

    return "\n".join(lines)


def insert_function_to_contract(
    function_code,
    template_path="forge/test/example.t.sol",
    output_path="forge/test/execute.t.sol",
):
    with open(template_path, "r", encoding="utf-8") as file:
        code = file.read()

    contract_pattern = r"\b(contract)\s+(\w+)\s*(is\s+\w+\s*,?\s*)*\{"
    match = re.search(contract_pattern, code, re.MULTILINE)
    if not match:
        return None  # No contract definition found

    # Find the index where the function should be inserted
    insertion_index = match.end()

    function_code = "\n    ".join([line for line in function_code.split("\n")])

    # Insert the function_code into the contract
    code = (
        code[:insertion_index]
        + "\n\n    "
        + function_code
        + "\n"
        + code[insertion_index:]
    )

    # Write the modified code back to the file
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(code)

    return code  # Return the modified code


def append_code_to_function(code, function_name, code_line):
    """
    Appends a given code line to the end of a specific function in the Solidity contract code.

    Parameters:
    - code (str): The original Solidity contract code.
    - function_name (str): The name of the function to which the code line will be appended.
    - code_line (str): The line of code to be appended.

    Returns:
    - str: The modified Solidity contract code with the code line appended to the function.
    """
    # Find the function definition
    function_pattern = (
        rf"\bfunction\s+{function_name}\s*\(([^)]*)\)\s*"
        rf"(public|private|internal|external)?\s*"
        rf"(view|pure)?\s*"
        rf"(returns\s*\([^)]*\))?\s*\{{"
    )
    match = re.search(function_pattern, code, re.DOTALL)
    if not match:
        return None  # No function definition found

    # Find the end of the function definition
    end_index = match.end()
    brace_count = 1
    for i in range(end_index, len(code)):
        if code[i] == "{":
            brace_count += 1
        elif code[i] == "}":
            brace_count -= 1
        if brace_count == 0:
            break

    # Insert the code_line before the closing brace of the function
    code = code[:i] + "\n        " + code_line + "\n    " + code[i:]

    return code


def add_modifier_to_code(code, modifier_code, modifier_name, target_function_names):
    """
    Inserts a given modifier code into the Solidity contract code and applies
    the modifier to specified functions.

    Parameters:
    - code (str): The original Solidity contract code.
    - modifier_code (str): The Solidity code for the modifier to be inserted.
    - modifier_name (str): The name of the modifier to be applied to specified functions.
    - target_function_names (list of str): The names of functions for modifier application.

    Returns:
    - str: The modified Solidity contract code with the modifier applied to specified functions.
    """
    # Find the start of the contract definition
    contract_pattern = r"\b(contract)\s+(\w+)\s*(is\s+\w+\s*,?\s*)*\{"
    match = re.search(contract_pattern, code)
    if not match:
        return None

    # Insert the modifier code at the start of the contract
    start_index = match.start()
    for i in range(start_index, len(code)):
        if code[i] == "{":
            code = code[: i + 1] + "\n" + modifier_code + code[i + 1 :]
            break

    # Apply the modifier to specified functions
    for target_function_name in target_function_names:
        function_pattern = rf"\bfunction\s+{target_function_name}\s*\(([^)]*)\)\s*(public|private|internal|external)?\s*(view|pure)?\s*(returns\s*\([^)]*\))?\s*\{{"
        matches = re.finditer(function_pattern, code)
        for match in matches:
            f_start_index = match.start()
            for i in range(f_start_index, len(code)):
                if code[i] == "{":
                    code = code[:i] + modifier_name + code[i:]
                    break

    return code


def insert_view_to_code(code):
    view_func = """    modifier viewWrapper() {
        _;
        view_func();
    }

    function view_func() public view {
        address agent_addr = address(this);
        address contract_addr = address(target_contract);
        console.log("agent_address:",agent_addr);
        console.log("agent_balance:",agent_addr.balance);
        console.log("contract_address:", contract_addr);
        console.log("contract_balance:", contract_addr.balance);
        console.log("owner:", target_contract.owner());
        console.log("@@@");
    }
    """

    # Insert the view modifier and function into the code
    modified_code = add_modifier_to_code(code, view_func, "viewWrapper", [])

    test_function_pattern = r"\bfunction\s+(test_\w+)\s*\([^)]*\)\s*[^{]*\{"

    matches = re.finditer(test_function_pattern, modified_code)
    for match in matches:
        function_name = match.group(1)
        # Apply the viewWrapper modifier to each test function found
        modified_code = add_modifier_to_code(
            modified_code, "", "viewWrapper", [function_name]
        )
        break  # Assuming we only modify the first found test function for demonstration

    return modified_code


def add_prefix_to_function(func_code, prefix):
    pattern = r"\bfunction\s+(\w+)\s*\([^)]*\)\s*[^{]*\{"
    matches = re.finditer(pattern, func_code)
    offset = 0
    for match in matches:
        func_name_start = match.start(1) + offset
        func_name_end = match.end(1) + offset
        func_name = match.group(1)
        new_func_name = prefix + func_name
        func_code = (
            func_code[:func_name_start] + new_func_name + func_code[func_name_end:]
        )
        offset += len(prefix)
    return func_code


def add_modifier_to_function(func_code, modifier_name):
    pattern = r"\bfunction\s+\w+\s*\([^)]*\)\s*[^{]*\{"
    matches = re.finditer(pattern, func_code)
    offset = 0
    for match in matches:
        if "view" in match.group(0):
            return func_code
        f_start_index = match.start() + offset
        for i in range(f_start_index, len(func_code)):
            if func_code[i] == "{":
                func_code = func_code[:i] + modifier_name + func_code[i:]
                offset += len(modifier_name) + 1
                break
    return func_code


def extract_function_name_with_prefix(code, prefix="test_"):
    test_function_pattern = r"\bfunction\s+(" + prefix + r"\w*)\s*\([^)]*\)\s*[^{]*\{"
    match = re.search(test_function_pattern, code)
    if match:
        return match.group(1)
    return None


def extract_function_definition(code, function_name, metadata_only=False):
    # Find the start of the contract definition
    pattern = r"\bfunction\s+" + re.escape(function_name) + r"\s*\([^)]*\)\s*[^{]*\{"
    match = re.search(pattern, code)
    if not match:
        return None

    start_index = match.start()

    # Count the braces to find the end of the contract definition
    brace_count = 0
    f_metadata = ""
    for i in range(start_index, len(code)):
        f_metadata += code[i]
        if code[i] == "{":
            if metadata_only:
                return f_metadata
            brace_count += 1
        elif code[i] == "}":
            brace_count -= 1
            if brace_count == 0:
                end_index = i + 1
                return code[start_index:end_index]

    return None


def extract_contract_name(code):
    contract_pattern = r"\bcontract\s+(\w+)"
    match = re.search(contract_pattern, code)
    if match:
        return match.group(1)
    return None


def extract_contract_definition(code, contract_name):
    # Find the start of the contract definition
    pattern = (
        r"\b(contract)\s+" + re.escape(contract_name) + r"\s*(is\s+\w+\s*,?\s*)*\{"
    )
    match = re.search(pattern, code)
    if not match:
        return None

    start_index = match.start()

    # Count the braces to find the end of the contract definition
    brace_count = 0
    for i in range(start_index, len(code)):
        if code[i] == "{":
            brace_count += 1
        elif code[i] == "}":
            brace_count -= 1
            if brace_count == 0:
                end_index = i + 1
                return code[start_index:end_index]

    return None


def number_of_real_lines(func_code):
    lines = func_code.split(";")
    if len(lines) == 1:
        return 0
    real_lines = 0
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line.startswith("//") and stripped_line != "":
            real_lines += 1
    return real_lines


if __name__ == "__main__":
    # Example usage
    solidity_code = """// SPDX-License-Identifier: MIT
    pragma solidity ^0.8.0;

    contract Fallback {
        mapping(address => uint) public contributions;
        address owner;

        constructor() {
            owner = msg.sender;
            contributions[msg.sender] = 1000 * (1 ether);
        }

        modifier onlyOwner() {
            require(msg.sender == owner, "caller is not the owner");
            _;
        }

        function contribute() public payable {
            require(msg.value < 0.001 ether);
            contributions[msg.sender] += msg.value;
            if (contributions[msg.sender] > contributions[owner]) {
                owner = msg.sender;
            }
        }

        function getContribution() public view returns (uint) {
            return contributions[msg.sender];
        }

        function withdraw() public onlyOwner {
            payable(owner).transfer(address(this).balance);
        }

        receive() external payable {
            require(msg.value > 0 && contributions[msg.sender] > 0);
            owner = msg.sender;
        }
    }

    interface IFallback {
        function contribute() external payable;
        function getContribution() external view returns (uint);
        function withdraw() external;
    }


    contract MyContract {
        Fallback private fallbackContract;

        constructor(address payable _fallbackContract) {
            fallbackContract = Fallback(_fallbackContract);
        }

        function contributeToFallback() public payable {
            fallbackContract.contribute{value: msg.value}();
        }

        function withdrawFromFallback() public {
            fallbackContract.withdraw();
        }
    }"""

    forge_test = """// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;
import "forge-std/Test.sol";
import "../src/target_contract.sol";

contract AgentContract is Test {
    TargetContract target_contract;

    function setUp() public viewWrapper {
        address owner = makeAddr("owner");
        vm.prank(owner);
        target_contract = new TargetContract();

        address victim = makeAddr("victim");
        vm.deal(victim, 1 ether);
        vm.prank(victim);
        target_contract.contribute{value: 0.0005 ether}();
    }

    // Send 0.01 ether to target contract without calling any functions: sendEther(0.01 ether);
    function sendEther(uint x) public viewWrapper {
        address payable target = payable(address(target_contract));
        (bool success, ) = target.call{value: x}("");
        require(success, "Transfer failed.");
    }

    modifier viewWrapper() {
        _;
        view_func();
    }

    function view_func() public view {
        address agent_addr = address(this);
        address contract_addr = address(target_contract);
        console.log("@agent_address:",agent_addr);
        console.log("@agent_balance:",agent_addr.balance);
        console.log("@contract_address:", contract_addr);
        console.log("@contract_balance:", contract_addr.balance);
        console.log("@owner:", target_contract.owner());
        console.log("@@@");
    }


}


    """

    # inserted_view = insert_view_to_code(forge_test)

    EXAMPLE_FUNCTION_CODE = """function contribute() public payable {
        target_contract.contribute{value: 0.0005 ether}();
        // Hello
        // Yo
    }"""
    print(number_of_real_lines(EXAMPLE_FUNCTION_CODE))
    test_view = "function test_view() public viewWrapper{}"
    insert_function_to_contract(
        test_view,
        "forge/test/example.t.sol",
        "forge/test/execute.t.sol",
    )

    VIEW_MODIFIER_CODE = """    modifier viewWrapper() {
        _;
        view_func();
    }

    function view_func() public view {
        address agent_addr = address(this);
        address contract_addr = address(target_contract);
        console.log("agent_address:",agent_addr);
        console.log("agent_balance:",agent_addr.balance);
        console.log("contract_address:", contract_addr);
        console.log("contract_balance:", contract_addr.balance);
        console.log("owner:", target_contract.owner());
        console.log("@@@");
    }
    """

    ret1 = insert_view_to_code(forge_test)
    ret2 = add_modifier_to_code(
        forge_test, VIEW_MODIFIER_CODE, "viewWrapper", ["test_contribute"]
    )
    # ret = append_code_to_function(
    #     forge_test,
    #     "setUp",
    #     "console.log(\"hello\");",
    # )
    # ret = extract_function_definition(function_code, "contribute", True)
    # main_func_name = transform_contract_public(solidity_code)
    # print(main_func_name)
    # contract_definition = extract_contract_definition(solidity_code, 'MyContract')
    # print(contract_definition)
    # return_dict = transform_contract_public(solidity_code)
    # print(return_dict)
