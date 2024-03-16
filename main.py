


import argparse

def main():
    parser = argparse.ArgumentParser(description="CLI tool for benchmarking.")
    parser.add_argument("--benchmark", action="store_true", default=False,
                        help="Enable benchmarking mode. Default is False.")
    parser.add_argument("--serial", action="store_true", default=False,
                        help="Run in serial mode. Default is False.")
    args = parser.parse_args()

    if args.benchmark:
        print("Benchmarking mode enabled.")
    else:
        print("Benchmarking mode not enabled.")

    if args.serial:
        print("Running in serial mode.")
    else:
        print("Running in parallel mode.")

if __name__ == "__main__":
    main()
