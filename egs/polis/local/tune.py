import argparse
import json
import os
import sys
from types import MethodType

from pyannote.audio import Model
from pyannote.audio import Pipeline
from pyannote.audio.pipelines import SpeakerDiarization
from pyannote.audio.tasks import Segmentation
from pyannote.database import get_protocol, FileFinder
from pyannote.pipeline import Optimizer
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint, RichProgressBar
from torch.optim import Adam

from sd_benchmark.logger import logger


def main(argv):
    logger.info("Starting")
    parser = argparse.ArgumentParser(description="Tune pyanote params")
    parser.add_argument("--ds", nargs='?', required=True, help="Dataset name")
    parser.add_argument("--out", nargs='?', required=True, help="Output file")
    parser.add_argument("--tune", nargs='?', required=False, default="msc",
                        help="Tune m - model, s - segnmentatiom threshold, c - clustering threshold")
    args = parser.parse_args(args=argv)

    logger.info(f"Ds: {args.ds}")
    logger.info(f"Tune params: {args.tune}")
    logger.info(f"Training segmentation")

    tune_epochs = 50

    pretrained_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization",
                                                   use_auth_token=os.getenv('HF_API_TOKEN'))
    dataset = get_protocol(args.ds, {"audio": FileFinder()})

    model = Model.from_pretrained("pyannote/segmentation", use_auth_token=os.getenv('HF_API_TOKEN'))
    task = Segmentation(dataset, duration=model.specifications.duration,
                        max_num_speakers=len(model.specifications.classes),
                        batch_size=32, num_workers=2, loss="bce", vad_loss="bce")
    model.task = task
    model.setup(stage="fit")

    default_params = pretrained_pipeline.parameters(instantiated=True)
    finetuned_model = model
    finetuned_segmentation_threshold = default_params["segmentation"]["threshold"]

    res = {
        "model": "default",
        "best_clustering_threshold": "default",
        "segmentation_threshold": "default"
    }

    if 'm' in args.tune:
        logger.info(f"Training segmentation model ")

        def configure_optimizers(self):
            return Adam(self.parameters(), lr=1e-4)

        model.configure_optimizers = MethodType(configure_optimizers, model)
        monitor, direction = task.val_monitor
        checkpoint = ModelCheckpoint(
            monitor=monitor,
            mode=direction,
            save_top_k=1,
            every_n_epochs=1,
            save_last=False,
            save_weights_only=False,
            filename="{epoch}",
            verbose=False,
        )
        early_stopping = EarlyStopping(
            monitor=monitor,
            mode=direction,
            min_delta=0.0,
            patience=10,
            strict=True,
            verbose=False,
        )

        callbacks = [RichProgressBar(), checkpoint, early_stopping]

        # we train for at most 20 epochs (might be shorter in case of early stopping)
        trainer = Trainer(accelerator="gpu",
                          callbacks=callbacks,
                          max_epochs=tune_epochs,
                          gradient_clip_val=0.5)
        trainer.fit(model)
        # save path to the best checkpoint for later use
        finetuned_model = checkpoint.best_model_path
        logger.info(f"Best segmentation Model: {finetuned_model}")
        logger.info(f"Tuning best_segmentation_threshold")
        res["model"] = finetuned_model,

    if 's' in args.tuned:
        pipeline = SpeakerDiarization(
            segmentation=finetuned_model,
            clustering="OracleClustering",
        )
        pipeline.freeze({"segmentation": {"min_duration_off": 0.0}})
        logger.info(f"Tuning segmentation threshold")
        optimizer = Optimizer(pipeline)
        dev_set = list(dataset.development())

        iterations = optimizer.tune_iter(dev_set, show_progress=False)

        for i, iteration in enumerate(iterations):
            print(f"Best segmentation threshold so far: {iteration['params']['segmentation']['threshold']}")
            if i > tune_epochs: break  # 50 iterations should give slightly better results
        finetuned_segmentation_threshold = optimizer.best_params["segmentation"]["threshold"]
        logger.info(f"finetuned_segmentation_threshold = {finetuned_segmentation_threshold}")
        res["segmentation_threshold"] = finetuned_segmentation_threshold

    if 'c' in args.tuned:
        logger.info(f"Tuning best_clustering_threshold")
        pipeline = SpeakerDiarization(
            segmentation=finetuned_model,
            embedding=pretrained_pipeline.embedding,
            embedding_exclude_overlap=pretrained_pipeline.embedding_exclude_overlap,
            clustering=pretrained_pipeline.klustering,
        )

        pipeline.freeze({
            "segmentation": {
                "threshold": finetuned_segmentation_threshold,
                "min_duration_off": 0.0,
            },
            "clustering": {
                "method": "centroid",
                "min_cluster_size": 15,
            },
        })

        optimizer = Optimizer(pipeline)
        iterations = optimizer.tune_iter(dev_set, show_progress=False)
        for i, iteration in enumerate(iterations):
            print(f"Best clustering threshold so far: {iteration['params']['clustering']['threshold']}")
            if i > tune_epochs: break  # 50 iterations should give slightly better results
        finetuned_clustering_threshold = optimizer.best_params['clustering']['threshold']
        logger.info(f"finetuned_clustering_threshold = {finetuned_clustering_threshold}")
        res["clustering_threshold"] = finetuned_clustering_threshold

    with open(args.out, 'w') as json_file:
        json.dump(res, json_file)

    logger.info("done")


if __name__ == "__main__":
    main(sys.argv[1:])
