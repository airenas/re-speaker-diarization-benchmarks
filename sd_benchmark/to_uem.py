import argparse
import os
import sys

from sd_benchmark.logger import logger
from sd_benchmark.utils.duration import duration


def main(argv):
    logger.info("Starting")
    parser = argparse.ArgumentParser(description="Prepares UEM files")
    parser.add_argument("--input", nargs='?', required=True, help="Audio file")
    parser.add_argument("--out_dir", nargs='?', required=True, help="Output dir")
    args = parser.parse_args(args=argv)

    file = args.input
    out_file = os.path.basename(file)
    base, _ = os.path.splitext(out_file)
    out_file = os.path.join(str(args.out_dir), base + ".uem")
    logger.info(f"In: {file}")
    logger.info(f"Out: {out_file}")

    f_len_secs = duration(args.input)

    base, _ = os.path.splitext(os.path.basename(file))
    with open(out_file, "w") as f:
        f.write(f"{base} 1 0.000 {f_len_secs}\n")


if __name__ == "__main__":
    main(sys.argv[1:])
