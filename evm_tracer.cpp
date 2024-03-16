#include <evmc/evmc.hpp>
#include <evmc/loader.h>
#include <evmc/mocked_host.hpp>

#include <evmone/evmone.h>
#include <evmone/vm.hpp>
#include <evmone/tracing.hpp>
#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>
#include <algorithm>
#include <cctype>
#include <getopt.h>
#include <string>

// Adjusted function to use evmone directly for tracing and include status code in output
std::string executeEVM(evmc::VM& vm, const evmc::bytes& bytecode, const evmc::bytes& calldata) {
    evmc_revision rev = EVMC_ISTANBUL; // Use the appropriate EVM revision
    evmc_address sender{};
    evmc_address destination{};
    int64_t gas = 10000000; // Set an appropriate gas limit

    evmc_message msg = {};
    msg.kind = EVMC_CALL;
    msg.sender = sender;
    msg.recipient = destination;
    msg.input_data = calldata.data();
    msg.input_size = calldata.size();
    msg.gas = gas;

    evmc::MockedHost host;
    evmc::Result result = vm.execute(host, rev, msg, bytecode.data(), bytecode.size());
    std::string status_code_str;
    switch (result.status_code) {
        case EVMC_SUCCESS:
            status_code_str = "Success";
            break;
        case EVMC_FAILURE:
            status_code_str = "Failure";
            break;
        case EVMC_REVERT:
            status_code_str = "Revert";
            break;
        case EVMC_OUT_OF_GAS:
            status_code_str = "Out of Gas";
            break;
        case EVMC_INVALID_INSTRUCTION:
            status_code_str = "Invalid Instruction";
            break;
        case EVMC_UNDEFINED_INSTRUCTION:
            status_code_str = "Undefined Instruction";
            break;
        case EVMC_STACK_OVERFLOW:
            status_code_str = "Stack Overflow";
            break;
        case EVMC_STACK_UNDERFLOW:
            status_code_str = "Stack Underflow";
            break;
        case EVMC_BAD_JUMP_DESTINATION:
            status_code_str = "Bad Jump Destination";
            break;
        case EVMC_INVALID_MEMORY_ACCESS:
            status_code_str = "Invalid Memory Access";
            break;
        case EVMC_CALL_DEPTH_EXCEEDED:
            status_code_str = "Call Depth Exceeded";
            break;
        case EVMC_STATIC_MODE_VIOLATION:
            status_code_str = "Static Mode Violation";
            break;
        case EVMC_PRECOMPILE_FAILURE:
            status_code_str = "Precompile Failure";
            break;
        case EVMC_CONTRACT_VALIDATION_FAILURE:
            status_code_str = "Contract Validation Failure";
            break;
        case EVMC_ARGUMENT_OUT_OF_RANGE:
            status_code_str = "Argument Out of Range";
            break;
        case EVMC_WASM_UNREACHABLE_INSTRUCTION:
            status_code_str = "WASM Unreachable Instruction";
            break;
        case EVMC_WASM_TRAP:
            status_code_str = "WASM Trap";
            break;
        case EVMC_INSUFFICIENT_BALANCE:
            status_code_str = "Insufficient Balance";
            break;
        case EVMC_INTERNAL_ERROR:
            status_code_str = "Internal Error";
            break;
        case EVMC_REJECTED:
            status_code_str = "Rejected";
            break;
        case EVMC_OUT_OF_MEMORY:
            status_code_str = "Out of Memory";
            break;
        default:
            status_code_str = "Unknown Error";
            break;
    }
    if (result.status_code == EVMC_FAILURE) {
        std::ofstream status_out("execution_status.json");
        status_out << "{\"status_code\": \"" << status_code_str << "\"}";
        status_out.close();
        throw std::runtime_error("EVM execution failed with status code: " + status_code_str);
    } else {
        std::ofstream status_out("execution_status.json");
        status_out << "{\"status_code\": \"" << status_code_str << "\"}";
        status_out.close();
        char full_path[PATH_MAX];
        realpath("execution_status.json", full_path);
        std::cout << "Status Code: " << status_code_str << std::endl;
        std::cout << "Execution status saved to: " << full_path << std::endl;
        return {result.output_data, result.output_data + result.output_size};
    }
}

// Takes in the EVM bytecode, calldata and then outputs a trace JSON file including execution status
void generateEVMTraceFile(
    const evmc::bytes& bytecode,
    const evmc::bytes& calldata,
    const std::string& trace_out_file_name)
{   
    auto* vm_ptr = evmc_create_evmone();
    evmc::VM vm{vm_ptr};

    // Set up tracing
    std::ofstream trace_out(trace_out_file_name);
    auto tracer = evmone::create_instruction_tracer(trace_out);
    static_cast<evmone::VM*>(vm_ptr)->add_tracer(std::move(tracer));

    try {
        auto result = executeEVM(vm, bytecode, calldata);
        std::cout << "Execution result: " << result << std::endl;
        char full_path[PATH_MAX];
        realpath(trace_out_file_name.c_str(), full_path);
        std::cout << "Trace JSON file saved to directory: " << full_path << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "Error during EVM execution: " << e.what() << std::endl;
        // Print out the error message
        std::cerr << "Error message: " << e.what() << std::endl;
    }
}


int main(int argc, char* argv[]) {
    std::string bytecode_hex;
    std::string calldata_hex;
    std::string trace_out_file_name;

    struct option long_options[] = {
        {"bytecode", required_argument, NULL, 'b'},
        {"calldata", required_argument, NULL, 'c'},
        {"tracefilename", required_argument, NULL, 't'},
        {NULL, 0, NULL, 0}
    };

    int option_index = 0;
    int option;
    while ((option = getopt_long(argc, argv, "b:c:t:", long_options, &option_index)) != -1) {
        switch (option) {
            case 'b':
                bytecode_hex = optarg;
                break;
            case 'c':
                calldata_hex = optarg;
                break;
            case 't':
                trace_out_file_name = optarg;
                break;
            default:
                std::cerr << "Usage: " << argv[0] << " --bytecode <bytecode_hex> --calldata <calldata_hex> --tracefilename <trace_out_file_name>\n";
                return 1;
        }
    }

    if (bytecode_hex.empty() || trace_out_file_name.empty()) {
        std::cerr << "Missing required arguments. Usage: " << argv[0] << " --bytecode <bytecode_hex> --calldata <calldata_hex> --tracefilename <trace_out_file_name>\n";
        return 1;
    }

    if (calldata_hex.empty()) {
        calldata_hex = ""; // Ensure calldata_hex is an empty string if not provided
    }
    // Convert hex string to bytes
    evmc::bytes bytecode;
    evmc::bytes calldata;
    auto hex_to_bytes = [](const std::string& hex) {
        evmc::bytes bytes;
        for (unsigned int i = 0; i < hex.length(); i += 2) {
            std::string byteString = hex.substr(i, 2);
            char byte = (char) strtol(byteString.c_str(), nullptr, 16);
            bytes.push_back(byte);
        }
        return bytes;
    };

    bytecode = hex_to_bytes(bytecode_hex);
    calldata = hex_to_bytes(calldata_hex);

    // Pass the converted values to generateEVMTraceFile
    generateEVMTraceFile(bytecode, calldata, trace_out_file_name);
}
