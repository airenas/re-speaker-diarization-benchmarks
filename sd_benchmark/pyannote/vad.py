import argparse
import os
import sys
import time

import numpy as np
import torch
from pyannote.audio import Pipeline, Model, Inference
from pyannote.audio.pipelines import VoiceActivityDetection

from sd_benchmark.logger import logger
from sd_benchmark.utils.duration import duration


def main(argv):
    logger.info("Starting")
    parser = argparse.ArgumentParser(description="Pyannote diarization")
    parser.add_argument("--input", nargs='?', required=True, help="wav file")
    parser.add_argument("--output_dir", nargs='?', required=True, help="rttm file")
    args = parser.parse_args(args=argv)

    f_len_secs = duration(args.input)

    logger.info("Init models")
    model = Model.from_pretrained("pyannote/segmentation@2.1",
                                  use_auth_token=os.getenv('HF_API_TOKEN'))
    pipeline = VoiceActivityDetection(segmentation=model)
    initial_params = {"onset": 0.4, "offset": 0.6,
                      "min_duration_on": 0.0, "min_duration_off": 0.0}
    pipeline.instantiate(initial_params)
    cuda = os.getenv('CUDA')  # 'cuda:0'
    if cuda and cuda != "cpu":
        pipeline = pipeline.to(torch.device(cuda))
    logger.info(f"Starting diarization: file len {f_len_secs:.2f}s on '{cuda}'")

    start_time = time.time()
    vad = pipeline(args.input)
    segments = list(vad.itertracks(yield_label=True))
    for v in segments:
        if v[0].duration > 10:
            print(v[0].start, v[0].duration)

    hook = lambda segmentation: np.max(segmentation, axis=2, keepdims=True)
    inference = Inference("pyannote/segmentation@2.1", use_auth_token=os.getenv('HF_API_TOKEN'), pre_aggregation_hook=hook)
    vad = inference(args.input)
    for frame, score in vad:
        t = frame.middle
        if 387 < t < (387 + 126):
            print(f"{t=:.3f} score={score}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    rt = elapsed_time / f_len_secs
    logger.info(f"Done diarization in {elapsed_time:.2f}s, rt = {rt:.2f}")

    base, _ = os.path.splitext(os.path.basename(args.input))
    out_file = os.path.join(args.output_dir, base + ".rttm")
    out_file = os.path.join(args.output_dir, base + ".time")
    with open(out_file, "w") as f:
        f.write(f"{base}\t{f_len_secs:.2f}\t{elapsed_time:.2f}\t{rt:.2f}\t{cuda}\n")


if __name__ == "__main__":
    main(sys.argv[1:])
