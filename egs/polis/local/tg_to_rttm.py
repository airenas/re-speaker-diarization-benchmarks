import argparse
import os
import sys

import textgrids

from sd_benchmark.logger import logger


class RTTMData:
    def __init__(self, label, start, dur):
        self.label = label
        self.dur = dur
        self.start = start


def try_join(rttm, r):
    start = r.start
    for cr in rttm:
        if cr.label == r.label and abs(cr.start + cr.dur - start) <= 0.01:  # 10ms
            dur = r.start + r.dur - cr.start
            if dur > cr.dur:
                cr.dur = dur
            return True
    return False


def join_same_speaker(rttm):
    res = []
    for r in rttm:
        if not try_join(res, r):
            res.append(r)
    return res


def check_label(label, change_z, base):
    label = label.strip().lower()
    if label == "z" and change_z:
        label = f"z_{base}"
    return label


def main(argv):
    logger.info("Starting")
    parser = argparse.ArgumentParser(description="Converts text grid to rttm")
    parser.add_argument("--input", nargs='?', required=True, help="Input file to parse")
    parser.add_argument("--out_dir", nargs='?', required=True, help="Output dir")
    parser.add_argument('--skip-3', action='store_true', default=False, help='Skip 3 speakers. Make no output file')
    parser.add_argument('--change-z', action='store_true', default=False, help='Change z speaker')
    args = parser.parse_args(args=argv)

    file = args.input
    out_file = file
    if out_file.startswith(os.sep):
        out_file = out_file[1:]
    base, _ = os.path.splitext(out_file)
    base = os.path.basename(base)
    out_file = os.path.join(str(args.out_dir), base + ".rttm")
    logger.info(f"In: {file}")
    logger.info(f"Out: {out_file}")

    res = []
    labels = set()

    def add_annotation(ann):
        start_time = ann.xmin
        duration = ann.xmax - start_time
        label = str(ann.text).strip().replace(" ", "")
        if label and not label.startswith("_"):
            labels.add(label)
            new_label = check_label(label, args.change_z, base)
            res.append(RTTMData(label=new_label, start=start_time, dur=duration))

    try:
        file_name, _ = os.path.splitext(os.path.basename(file))
        grid = textgrids.TextGrid(file)
        p_grid_name = "Policija"
        for g in grid:
            if g == "Policinikas":
                p_grid_name = "Policinikas"
        if len(grid) > 2:
            logger.info("3 grids")
            raise RuntimeError("3 grids")

        for annotation in grid[p_grid_name]:
            add_annotation(annotation)
        for annotation in grid['Klientas']:
            add_annotation(annotation)

        res = sorted(res, key=lambda d: d.start)

        res = join_same_speaker(res)

        rttm_lines = []
        for r in res:
            rttm_line = f"SPEAKER {file_name} 1 {r.start:.3f} {r.dur:.3f} <NA> <NA> {r.label} <NA> <NA>"
            rttm_lines.append(rttm_line)

        logger.info(f"LABELS: {labels}")

        # if len(labels) < 2:
        #     logger.info(f"!!!!!!!!!!!!!!!!!! 1 speaker {base}")
        #     raise RuntimeError("1 speaker")
        if len(labels) > 2 and args.skip_3:
            logger.info(f"Skip output More than 2 LABELS: {labels}")
        else:
            with open(out_file, "w") as file:
                [file.write(line + '\n') for line in rttm_lines]
        logger.info("done")

    except Exception as e:
        logger.error(f"Error processing file {args.input}: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
