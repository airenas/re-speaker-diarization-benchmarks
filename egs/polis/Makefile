include Makefile.options
include $(cfg)
log?=INFO
python_cmd=PYTHONPATH=../../ LOG_LEVEL=$(log) python
CUDA?=cpu
variant?=mini
set?=test
list?=./data/$(set).$(variant).txt
PYANNOTE_DATABASE_CONFIG=data/database.yaml
epoch?=50
############################################################
corpus_dir=corpus
work_dir?=work
audio_data?=

$(corpus_dir)/.done/ $(corpus_dir)/audio $(corpus_dir)/audio.in $(work_dir)/rttm corpus $(work_dir)/pyannote \
	$(work_dir)/.done $(work_dir)/tuned $(work_dir):
	mkdir -p $@

$(corpus_dir)/.done/.audio.in: $(audio_data) | $(corpus_dir)/.done/ $(corpus_dir)/audio.in
	unzip $^ -d $(corpus_dir)/audio
	find $(corpus_dir)/audio -type f -name "*.wav" -print0 | xargs -0 -I {} sh -c "mv {} $(corpus_dir)/audio.in"
	touch $@

$(corpus_dir)/.done/.audio: $(corpus_dir)/.done/.audio.in | $(corpus_dir)/.done/ $(corpus_dir)/audio
	ls -1 $(corpus_dir)/audio.in/*.wav | xargs -n 1 basename | xargs -I {} sh -c "ffmpeg -i $(corpus_dir)/audio.in/{} $(corpus_dir)/audio/{}"
	touch $@

$(corpus_dir)/.done/.rttm: $(corpus_dir)/.done/.audio
	find $(corpus_dir)/audio/anotuoti -type f -name "*.TextGrid" -print0 | xargs -0 -I {} sh -c "$(python_cmd) local/tg_to_rttm.py --input {} --skip-3 --out_dir $(corpus_dir)/audio --change-z"
	touch $@

$(corpus_dir)/.done/.uem: $(corpus_dir)/.done/.audio
	ls -1 $(corpus_dir)/audio.in/*.wav | xargs -n 1 basename | xargs -I {} sh -c "$(python_cmd) ../../sd_benchmark/to_uem.py --input $(corpus_dir)/audio/{} --out_dir $(corpus_dir)/audio"
	touch $@

$(corpus_dir)/all.list: $(corpus_dir)/.done/.rttm
	@find $(corpus_dir)/audio -type f -name "*.rttm" | xargs -n1 -I {} basename {} .rttm | sort > $@

$(corpus_dir)/.done/.sets: $(corpus_dir)/all.list
	$(python_cmd) local/prepare_sets.py --input $(corpus_dir)/all.list --out-dir data
	touch $@

prepare/data: $(corpus_dir)/.done/.audio $(corpus_dir)/.done/.rttm $(corpus_dir)/.done/.uem $(corpus_dir)/.done/.sets

prepare/list: 
	@find $(corpus_dir)/audio -type f -name "*.wav" | xargs -n1 -I {} basename {} .wav | sort

diarization/%:
	cat $(list) | xargs -n1 -I {} sh -c "$(MAKE) $(work_dir)/$*/{}.rttm"

$(work_dir)/pyannote/%.rttm: | $(work_dir)/pyannote
	$(python_cmd) ../../sd_benchmark/pyannote/diarization.py --input $(corpus_dir)/audio/$*.wav --output_dir $(work_dir)/pyannote $(dia_params)

calc/err/%:
	cat $(list) | xargs -n1 -I {} sh -c "$(MAKE) $(work_dir)/$*/{}.err"
	$(MAKE) show/err/$*

show/err/%:
	xargs -a $(list) -I {} cat $(work_dir)/$*/{}.err
	xargs -a $(list) -I {} cat $(work_dir)/$*/{}.err | $(python_cmd) ../../sd_benchmark/calc_total_err.py

show/time/%:
	xargs -a $(list) -I {} cat $(work_dir)/$*/{}.time
	xargs -a $(list) -I {} cat $(work_dir)/$*/{}.time | $(python_cmd) ../../sd_benchmark/calc_total_time.py

$(work_dir)/pyannote/%.err: $(work_dir)/pyannote/%.rttm
	$(python_cmd) ../../sd_benchmark/pyannote/der.py --audio $(corpus_dir)/audio/$*.wav --f1 $(corpus_dir)/audio/$*.rttm --f2 $^ --output $@

run: diarization/pyannote calc/err/pyannote
############################################################
show/db:
	pyannote-database info POLIS.SpeakerDiarization.$(variant)
tune/model: $(work_dir)/tuned.json
$(work_dir)/tuned.json: | $(work_dir)
	$(python_cmd) local/tune.py --ds POLIS.SpeakerDiarization.$(variant) --out $(work_dir)/tuned.json --tune=$(tune_params) --epoch=$(epoch)
diarization/tuned:
	cat $(list) | xargs -n1 -I {} sh -c "$(MAKE) $(work_dir)/tuned/{}.rttm"

$(work_dir)/tuned/%.rttm: $(work_dir)/tuned.json | $(work_dir)/tuned
	$(python_cmd) local/diarization.py --input $(corpus_dir)/audio/$*.wav --output_dir $(work_dir)/tuned $(dia_params) \
		--model-config $(work_dir)/tuned.json
$(work_dir)/tuned/%.err: $(work_dir)/tuned/%.rttm
	$(python_cmd) ../../sd_benchmark/pyannote/der.py --audio $(corpus_dir)/audio/$*.wav --f1 $(corpus_dir)/audio/$*.rttm --f2 $^ --output $@
run/tuned: diarization/tuned calc/err/tuned		
############################################################
clean:
	rm -rf $(work_dir)/pyannote $(work_dir)/tuned $(work_dir)/tuned.json

clean/corpus:
	rm -rf $(corpus_dir)

.EXPORT_ALL_VARIABLES:	
