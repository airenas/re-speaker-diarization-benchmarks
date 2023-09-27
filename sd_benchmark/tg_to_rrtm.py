import argparse
import os
import sys

import textgrids

from sd_benchmark.logger import logger


def main(argv):
    logger.info("Starting")
    parser = argparse.ArgumentParser(description="Converts text grid to rrtm")
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
    out_file = os.path.join(str(args.out_dir), base + ".rrtm")
    logger.info(f"In: {file}")
    logger.info(f"Out: {out_file}")

    try:
        file_name = os.path.splitext(os.path.basename(file))
        rrtm_lines = []
        grid = textgrids.TextGrid(file)
        for annotation in grid['S']:
            start_time = annotation.xmin / 1000
            duration = annotation.xmax / 1000 - start_time
            label = annotation.text

            if label and label != "_S":
                rrtm_line = f"SPEAKER {file_name} 1 {start_time:.6f} {duration:.3f} <NA> <NA> {label} <NA> <NA>"
                rrtm_lines.append(rrtm_line)

        with open(out_file, "w") as file:
            [file.write(line + '\n') for line in rrtm_lines]
        logger.info("done")
    except Exception as e:
        logger.error(f"Error processing file {args.input}: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
