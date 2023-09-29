import argparse
import os
import sys

import textgrids

from sd_benchmark.logger import logger

class Seg:
    def __init__(self, start, dur, sp):
        self.sp = sp
        self.dur = int(dur)
        self.start = int(start)


def main(argv):
    logger.info("Starting")
    parser = argparse.ArgumentParser(description="Converts text grid to rrtm")
    parser.add_argument("--input", nargs='?', required=True, help="Input file to parse")
    parser.add_argument("--output", nargs='?', required=True, help="Output dir")
    args = parser.parse_args(args=argv)

    file = args.input
    out_file = args.output
    file_name, _ = os.path.splitext(out_file)
    logger.info(f"In: {file}")
    logger.info(f"Out: {out_file}")

    try:
        segs = []
        with open(file, "r") as f:
            for line in file:
                line = line.strip()
                if line:
                    splits = line.split(" ")
                    segs.append(Seg(start=splits[2], dur=splits[3], sp=splits[7]))

        segs = sorted(segs, key=lambda d: d.start)

        rrtm_lines = []
        for s in segs:
            start_time = s.start/100
            duration = s.dur/100
            label = s.sp

            rrtm_line = f"SPEAKER {file_name} 1 {start_time:.3f} {duration:.3f} <NA> <NA> {label} <NA> <NA>"
            rrtm_lines.append(rrtm_line)

        with open(out_file, "w") as file:
            [file.write(line + '\n') for line in rrtm_lines]
        logger.info("done")
    except Exception as e:
        logger.error(f"Error processing file {args.input}: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
