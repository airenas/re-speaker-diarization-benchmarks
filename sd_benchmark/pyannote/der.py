import argparse
import os
import sys

from pyannote.database.util import load_rttm
from pyannote.metrics.diarization import DiarizationErrorRate

from sd_benchmark.logger import logger


def main(argv):
    logger.info("Starting")
    parser = argparse.ArgumentParser(description="Show speakers")
    parser.add_argument("--f1", nargs='?', required=True, help="f1 file")
    parser.add_argument("--f2", nargs='?', required=True, help="f2 file")
    parser.add_argument("--output", nargs='?', required=True, help="error")
    args = parser.parse_args(args=argv)

    logger.info(f"cmp f1: {args.f1}")
    logger.info(f"cmp f2: {args.f2}")
    metric = DiarizationErrorRate()
    _, d1 = load_rttm(args.f1).popitem()
    _, d2 = load_rttm(args.f2).popitem()
    der = metric(d1, d2)
    logger.info(f'diarization error rate = {100 * der:.1f}%')
    base, _ = os.path.splitext(os.path.basename(args.f2))
    with open(args.output, "w") as f:
        f.write(f'{base}\t{der:.2f}\n')


if __name__ == "__main__":
    main(sys.argv[1:])
