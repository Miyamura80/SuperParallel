import random
import pprint


def run_serial(benchmark=False):
    pass


def run_superparallel(benchmark=False):

    addresses = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    contracts = {
        "X": {"_allowances": 2, "_balances": 1}, 
        "Y": {"_allowances": 2, "_balances": 1},
        "Z": {"_allowances": 2, "_balances": 1},
    }

    n_addr = len(addresses)

    # Initialize a Bloom filter with a capacity of 1000 items
    # and a false positive rate of 0.01
    bloom_filters = {
        contract_addr : 
        [
            [
                False for _ in range(n_addr)
            ]
            for _ in range(n_addr)            
        ]
        if bloom_filter_dim == 2 
        else [False for _ in range(n_addr)]
        for contract_addr, bloom_filter_dim in contracts.items()
    }


    mempool = [
        {
            "to": random.choice(list(contracts.keys())), 
            "from": random.choice(addresses), 
            "data": "0x"
        } 
        for _ in range(round(len(addresses) * len(contracts) * 0.8))
    ]

    pprint.pprint(mempool)

    




if __name__ == "__main__":
    run_superparallel()

