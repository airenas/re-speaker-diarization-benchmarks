import argparse
import sys

from sd_benchmark.logger import logger


def main(argv):
    logger.info("Starting")
    parser = argparse.ArgumentParser(description="Calculate avg rt")
    args = parser.parse_args(args=argv)

    len_s, dur = 0, 0
    for line in sys.stdin:
        line = line.strip()
        if line:
            splits = line.split("\t")
            if len(splits) < 4:
                raise RuntimeError("wrong line " + line)
            len_s += float(splits[1])
            dur += float(splits[2])

    print(f"total\t{len_s:.2f}\t{dur:.2f}\t{dur / len_s:.2f}\n")


if __name__ == "__main__":
    main(sys.argv[1:])
