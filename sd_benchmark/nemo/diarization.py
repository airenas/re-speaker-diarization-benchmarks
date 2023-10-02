import argparse
import os
import sys
import time

from nemo.collections.asr.models import NeuralDiarizer
from omegaconf import OmegaConf

from sd_benchmark.logger import logger
from sd_benchmark.utils.duration import duration


def prepare_manifest(file, output_dir):
    file_name, _ = os.path.splitext(os.path.basename(file))
    import json
    meta = {
        'audio_filepath': file,
        'offset': 0,
        'duration': None,
        'label': 'infer',
        'text': '-',
        'num_speakers': None,
        'rttm_filepath': None,
        'uem_filepath': None
    }
    res = os.path.join(output_dir, file_name + ".manifest.json")
    with open(res, 'w') as fp:
        json.dump(meta, fp)
        fp.write('\n')
    return res


def main(argv):
    logger.info("Starting")
    parser = argparse.ArgumentParser(description="Nemo diarization")
    parser.add_argument("--input", nargs='?', required=True, help="wav file")
    parser.add_argument("--output_dir", nargs='?', required=True, help="rttm file")
    args = parser.parse_args(args=argv)

    f_len_secs = duration(args.input)

    logger.info("Init models")

    manifest_file = prepare_manifest(args.input, args.output_dir)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config = OmegaConf.load(os.path.join(script_dir, "diar_infer_telephonic.yaml"))

    config.diarizer.manifest_filepath = manifest_file
    config.diarizer.out_dir = args.output_dir

    config.diarizer.speaker_embeddings.model_path =  'titanet_large'
    config.diarizer.oracle_vad = False  # compute VAD provided with model_path to vad config
    config.diarizer.clustering.parameters.oracle_num_speakers = False

    # Here, we use our in-house pretrained NeMo VAD model
    config.diarizer.vad.model_path = 'vad_multilingual_marblenet'
    config.diarizer.vad.parameters.onset = 0.8
    config.diarizer.vad.parameters.offset = 0.6
    config.diarizer.vad.parameters.pad_offset = -0.05

    config.diarizer.msdd_model.model_path = 'diar_msdd_telephonic'  # Telephonic speaker diarization model
    config.diarizer.msdd_model.parameters.sigmoid_threshold = [0.7, 1.0]  # Evaluate with T=0.7 and T=1.0

    cuda = os.getenv('CUDA')  # 'cuda:0'
    if cuda:
        config.device = cuda
    logger.info(f"Starting diarization: file len {f_len_secs:.2f}s on '{cuda}'")

    system_vad_msdd_model = NeuralDiarizer(cfg=config)

    start_time = time.time()
    system_vad_msdd_model.diarize()
    end_time = time.time()
    elapsed_time = end_time - start_time
    rt = elapsed_time / f_len_secs
    logger.info(f"Done diarization in {elapsed_time:.2f}s, rt = {rt:.2f}")

    base, _ = os.path.splitext(os.path.basename(args.input))

    out_file = os.path.join(args.output_dir, base + ".rttm")
    expected_out_file = os.path.join(args.output_dir, "pred_rttms", base + ".rttm")
    with open(expected_out_file, "r") as fp:
        with open(out_file, "w") as f:
            f.write(fp.read())

    out_file = os.path.join(args.output_dir, base + ".time")
    with open(out_file, "w") as f:
        f.write(f"{base}\t{f_len_secs:.2f}\t{elapsed_time:.2f}\t{rt:.2f}\t{cuda}\n")


if __name__ == "__main__":
    main(sys.argv[1:])
