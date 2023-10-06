import argparse
import os
import sys
import time

from simple_diarizer.diarizer import Diarizer

from sd_benchmark.logger import logger
from sd_benchmark.utils.duration import duration


def main(argv):
    logger.info("Starting")
    parser = argparse.ArgumentParser(description="Simple diarization")
    parser.add_argument("--input", nargs='?', required=True, help="wav file")
    parser.add_argument("--output_dir", nargs='?', required=True, help="rttm file")
    args = parser.parse_args(args=argv)

    f_len_secs = duration(args.input)

    cuda = os.getenv('CUDA')  # 'cuda:0'
    # if cuda:
    #     config.device = cuda
    # logger.info(f"Starting diarization: file len {f_len_secs:.2f}s on '{cuda}'")

    base, _ = os.path.splitext(os.path.basename(args.input))
    out_file = os.path.join(args.output_dir, base + ".rttm")
    diarization = Diarizer(embed_model='xvec', cluster_method='ahc', window=1.5, period=0.75)
    start_time = time.time()
    segments = diarization.diarize(args.input, num_speakers=None, threshold=1e-1, outfile=out_file)
    end_time = time.time()
    elapsed_time = end_time - start_time
    rt = elapsed_time / f_len_secs
    logger.info(f"Done diarization in {elapsed_time:.2f}s, rt = {rt:.2f}")

    out_file = os.path.join(args.output_dir, base + ".time")
    with open(out_file, "w") as f:
        f.write(f"{base}\t{f_len_secs:.2f}\t{elapsed_time:.2f}\t{rt:.2f}\t{cuda}\n")


if __name__ == "__main__":
    main(sys.argv[1:])
