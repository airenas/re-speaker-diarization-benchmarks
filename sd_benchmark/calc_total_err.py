import argparse
import sys

from sd_benchmark.logger import logger


def main(argv):
    logger.info("Starting")
    parser = argparse.ArgumentParser(description="Calculate avg der")
    args = parser.parse_args(args=argv)

    len_s, avg_der, avf_der_nosil = 0, 0, 0
    for line in sys.stdin:
        line = line.strip()
        if line:
            splits = line.split("\t")
            if len(splits) < 4:
                raise RuntimeError("wrong line " + line)
            len_f = float(splits[1])
            len_s += len_f
            avg_der += float(splits[2]) * len_f
            avf_der_nosil += float(splits[3]) * len_f

    print(f"total\t{len_s:.2f}\t{avg_der / len_s:.2f}\t{avf_der_nosil / len_s:.2f}\n")


if __name__ == "__main__":
    main(sys.argv[1:])
