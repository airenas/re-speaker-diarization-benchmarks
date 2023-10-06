import argparse
import os
import sys
import time

from sd_benchmark.logger import logger
from sd_benchmark.utils.duration import duration


def load_time(file):
    with open(file, 'r') as f:
        nanoseconds = int(f.readline())
    seconds = nanoseconds / 1_000_000_000
    return time.time() + seconds


def main(argv):
    logger.info("Starting")
    parser = argparse.ArgumentParser(description="Calculate elapsed time")
    parser.add_argument("--input", nargs='?', required=True, help="wav file")
    parser.add_argument("--start", nargs='?', required=True, help="start time file")
    parser.add_argument("--end", nargs='?', required=True, help="end time file")
    parser.add_argument("--output", nargs='?', required=True, help="output time file")
    args = parser.parse_args(args=argv)

    f_len_secs = duration(args.input)

    start_time = load_time(args.start)
    end_time = load_time(args.end)
    elapsed_time = end_time - start_time
    rt = elapsed_time / f_len_secs
    base, _ = os.path.splitext(os.path.basename(args.input))
    with open(args.output, "w") as f:
        f.write(f"{base}\t{f_len_secs:.2f}\t{elapsed_time:.2f}\t{rt:.2f}\tcpu\n")


if __name__ == "__main__":
    main(sys.argv[1:])
