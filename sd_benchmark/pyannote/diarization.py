import argparse
import os
import sys
import time

import torch
from pyannote.audio import Pipeline

from sd_benchmark.logger import logger
from sd_benchmark.utils.duration import duration


def main(argv):
    logger.info("Starting")
    parser = argparse.ArgumentParser(description="Pyannote diarization")
    parser.add_argument("--input", nargs='?', required=True, help="wav file")
    parser.add_argument("--output_dir", nargs='?', required=True, help="rttm file")
    parser.add_argument("--speakers", nargs='?', default=None, type=int, required=False, help="speakers")
    parser.add_argument("--speakers-min", nargs='?', default=None, type=int, required=False, help="speakers from")
    parser.add_argument("--speakers-max", nargs='?', default=None, type=int, required=False, help="speakers to")
    parser.add_argument("--model", nargs='?', default="pyannote/speaker-diarization@2.1", type=str, help="model version")
    args = parser.parse_args(args=argv)

    f_len_secs = duration(args.input)

    logger.info(f"Init models: {args.model}")
    pipeline = Pipeline.from_pretrained(args.model, use_auth_token=os.getenv('HF_API_TOKEN'))
    cuda = os.getenv('CUDA')  # 'cuda:0'
    if cuda and cuda != "cpu":
        pipeline = pipeline.to(torch.device(cuda))
    logger.info(
        f"Starting diarization: file len {f_len_secs:.2f}s on '{cuda}', speakers {args.speakers} [{args.speakers_min}-{args.speakers_max}]")

    start_time = time.time()
    diarization = pipeline(args.input, num_speakers=args.speakers, min_speakers=args.speakers_min,
                           max_speakers=args.speakers_max)
    end_time = time.time()
    elapsed_time = end_time - start_time
    rt = elapsed_time / f_len_secs
    logger.info(f"Done diarization in {elapsed_time:.2f}s, rt = {rt:.2f}")

    base, _ = os.path.splitext(os.path.basename(args.input))
    out_file = os.path.join(args.output_dir, base + ".rttm")
    with open(out_file, "w") as f:
        diarization.write_rttm(f)
    out_file = os.path.join(args.output_dir, base + ".time")
    with open(out_file, "w") as f:
        f.write(f"{base}\t{f_len_secs:.2f}\t{elapsed_time:.2f}\t{rt:.2f}\t{cuda}\n")


if __name__ == "__main__":
    main(sys.argv[1:])
