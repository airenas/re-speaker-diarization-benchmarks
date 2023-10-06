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
# if requirements does not work
# pip install Cython nemo_toolkit[all]
```

### data

Initial data expected to be located in `./data` dir

```bash
make prepare/data
```

### diariazation

```bash
make calc-err/pyannote
```
