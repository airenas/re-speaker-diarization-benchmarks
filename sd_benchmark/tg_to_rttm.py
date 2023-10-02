import argparse
import os
import sys

import textgrids

from sd_benchmark.logger import logger


def main(argv):
    logger.info("Starting")
    parser = argparse.ArgumentParser(description="Converts text grid to rttm")
    parser.add_argument("--input", nargs='?', required=True, help="Input file to parse")
    parser.add_argument("--out_dir", nargs='?', required=True, help="Output dir")
    parser.add_argument("--prefix", nargs='?', required=True, help="Input prefix to trim")
    args = parser.parse_args(args=argv)

    file = args.input
    out_file = file
    if out_file.startswith(args.prefix):
        out_file = out_file[len(args.prefix):]
    if out_file.startswith(os.sep):
        out_file = out_file[1:]
    base, _ = os.path.splitext(out_file)
    out_file = os.path.join(str(args.out_dir), base + ".rttm")
    logger.info(f"In: {file}")
    logger.info(f"Out: {out_file}")

    try:
        file_name, _ = os.path.splitext(os.path.basename(file))
        rttm_lines = []
        grid = textgrids.TextGrid(file)
        for annotation in grid['S']:
            start_time = annotation.xmin
            duration = annotation.xmax - start_time
            label = annotation.text

            if label and label != "_S":
                rttm_line = f"SPEAKER {file_name} 1 {start_time:.3f} {duration:.3f} <NA> <NA> {label} <NA> <NA>"
                rttm_lines.append(rttm_line)

        with open(out_file, "w") as file:
            [file.write(line + '\n') for line in rttm_lines]
        logger.info("done")
    except Exception as e:
        logger.error(f"Error processing file {args.input}: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
