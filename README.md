# re-speaker-diarization-benchmark
The repo tests several speaker diarization tools on our local corpus:
- [] LIUM
- [] 
- []
- []

## DER results

*...to be defined*

## Preparation 

### env

Tested with Python: 
 - 3.11
 - 3.10 (Nemo)

#### Pyannote
```bash
conda create -n spdia2023 python=3.11
conda activate spdia2023
pip install -r requirements.txt
```

#### Nemo
```bash
conda create -n spdia-nemo2023 python=3.10
conda activate spdia-nemo2023
pip install -r requirements-nemo.txt
# if requirements does not work
# pip install Cython nemo_toolkit[all]
```

#### Simple Diarizer
```bash
conda create -n spdia-sd2023 python=3.11
conda activate spdia-sd2023
pip install -r requirements-simple-diarizer.txt
```

### data

Initial data expected to be located in `./data` dir

```bash
make prepare/data
```

### diarization

```bash
make calc-err/pyannote calc-err/lium calc-err/kaldi
```

### Results

| lib       | der       | der (-false alarm) | rt       | Info | VAD | Embedings/model | Clustering
|-----------|-----------|--------------|-----------|--------| ---| --| -- |
| pyannote  | 0.30 | 0.18| 1.93 | local e2e + multi stage | CG-LSTM | pyannote/speaker-diarization@2.1 | 
| nemo | 0.31 |	0.24 | 0.36 | multi stage | huseinzol05/nemo-vad-multilingual-marblenet  | nvidia/speakerverification_en_titanet_large | Multi-scale Diarizerion Decoder 
| kaldi (bbc)| 0.42	| 0.31 | 0.05 | multi stage | based on xvectors | xvectors
| simple diarizer | 0.45 | 0.35 | 0.09 | multi stage | snakers4/silero-vad | xvectors - speechbrain/spkrec-xvect-voxceleb | Agglomerative Hierarchical Clustering
| lium| 0.57 | 0.37| 0.33 | multi stage |
