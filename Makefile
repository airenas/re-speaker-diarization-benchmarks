include Makefile.options
log?=INFO
python_cmd=PYTHONPATH=./ LOG_LEVEL=$(log) python
CUDA?=cuda:0
list?=./work/min.list
############################################################
corpus_dir=./corpus
work_dir=./work
audio_data=./data/WAV16.ZIP
textgrid_data=./data/GRID-SPK.ZIP

$(corpus_dir)/.done/ $(corpus_dir)/audio $(corpus_dir)/grids $(work_dir)/rttm corpus $(work_dir)/pyannote $(work_dir)/lium \
	$(work_dir)/.done $(work_dir)/nemo $(work_dir)/nemo2 $(work_dir)/sd $(work_dir)/kaldi $(work_dir)/kaldi/out:
	mkdir -p $@

$(corpus_dir)/.done/.audio: $(audio_data) | $(corpus_dir)/.done/ $(corpus_dir)/audio
	unzip $^ -d $(corpus_dir)/audio
	find $(corpus_dir)/audio -type f -name "*.wav" -print0 | xargs -0 -I {} sh -c "mv {} $(corpus_dir)/audio/"
	touch $@

$(corpus_dir)/.done/.grids: $(textgrid_data) | $(corpus_dir)/.done/ $(corpus_dir)/grids
	unzip $^ -d $(corpus_dir)/grids
	find $(corpus_dir)/grids -type f -name "*.TextGrid" -print0 | xargs -0 -I {} sh -c "mv {} $(corpus_dir)/grids/"
	touch $@

$(corpus_dir)/.done/.rttm: $(corpus_dir)/.done/.grids $(corpus_dir)/.done/.audio
	find $(corpus_dir)/grids -type f -name "*.TextGrid" -print0 | xargs -0 -I {} sh -c "$(python_cmd) sd_benchmark/tg_to_rttm.py --input {} --out_dir $(corpus_dir)/audio --prefix $(corpus_dir)/grids"
	touch $@

prepare/data: $(corpus_dir)/.done/.audio $(corpus_dir)/.done/.rttm

prepare/list: 
	@find $(corpus_dir)/audio -type f -name "*.wav" | xargs -n1 -I {} basename {} .wav | sort

diarization/%:
	cat $(list) | xargs -n1 -I {} sh -c "$(MAKE) $(work_dir)/$*/{}.rttm"

diarization/lium:
	cat $(list) | xargs -n1 -I {} sh -c "$(MAKE) $(work_dir)/lium/{}.rttm $(work_dir)/lium/{}.seg"

diarization/kaldi-bbc:
	cat $(list) | xargs -n1 -I {} sh -c "$(MAKE) $(work_dir)/kaldi/{}.rttm"

$(work_dir)/.done/.lium-docker: | $(work_dir)/.done/
	cd lium && $(MAKE) dbuild
	touch $@

$(work_dir)/pyannote/%.rttm: | $(work_dir)/pyannote
	$(python_cmd) sd_benchmark/pyannote/diarization.py --input $(corpus_dir)/audio/$*.wav --output_dir $(work_dir)/pyannote

$(work_dir)/nemo/%.rttm: | $(work_dir)/nemo
	$(python_cmd) sd_benchmark/nemo/diarization_clustering.py --input $(corpus_dir)/audio/$*.wav --output_dir $(work_dir)/nemo

$(work_dir)/nemo2/%.rttm: | $(work_dir)/nemo2
	$(python_cmd) sd_benchmark/nemo/diarization.py --input $(corpus_dir)/audio/$*.wav --output_dir $(work_dir)/nemo2

$(work_dir)/sd/%.rttm: | $(work_dir)/sd
	$(python_cmd) sd_benchmark/simple_diarizer/diarization.py --input $(corpus_dir)/audio/$*.wav --output_dir $(work_dir)/sd


$(work_dir)/lium/%.seg: $(work_dir)/.done/.lium-docker | $(work_dir)/lium
	echo `date +%s%N` > $(work_dir)/lium/$*.time.start
	docker run --rm -i -v $$(pwd)/$(corpus_dir)/audio:/in -v $$(pwd)/$(work_dir)/lium:/res airenas/lium:0.1.0 ./run.sh /in/$*.wav /res/$*.seg
	echo `date +%s%N` > $(work_dir)/lium/$*.time.end
	$(python_cmd) sd_benchmark/calc_time.py --input $(corpus_dir)/audio/$*.wav --start $(work_dir)/lium/$*.time.start --end $(work_dir)/lium/$*.time.end --output $(work_dir)/lium/$*.time

$(work_dir)/lium/%.rttm: $(work_dir)/lium/%.seg | $(work_dir)/lium
	$(python_cmd) sd_benchmark/seg_to_rttm.py --input $(work_dir)/lium/$*.seg --output $(work_dir)/lium/$*.rttm

$(work_dir)/kaldi/%.stm: | $(work_dir)/kaldi
	DURATION=$$(ffprobe -i $(corpus_dir)/audio/$*.wav -show_entries format=duration -v quiet -of csv="p=0"); \
	echo "$* 0 $* 0.00 $${DURATION} <label> _" > $@_
	mv $@_ $@
$(work_dir)/kaldi/%.rttm: $(work_dir)/kaldi/%.stm | $(work_dir)/kaldi/out
	echo `date +%s%N` > $(work_dir)/kaldi/$*.time.start
	docker run -v $$(pwd):/data bbcrd/bbc-speech-segmenter ./run-segmentation.sh /data/$(corpus_dir)/audio/$*.wav /data/$(work_dir)/kaldi/$*.stm /data/$(work_dir)/kaldi/out
	echo `date +%s%N` > $(work_dir)/kaldi/$*.time.end
	cp $(work_dir)/kaldi/out/diarize.rttm $(work_dir)/kaldi/$*.rttm
	$(python_cmd) sd_benchmark/calc_time.py --input $(corpus_dir)/audio/$*.wav --start $(work_dir)/kaldi/$*.time.start --end $(work_dir)/kaldi/$*.time.end --output $(work_dir)/kaldi/$*.time


calc-err/pyannote:
	cat $(list) | xargs -n1 -I {} sh -c "$(MAKE) $(work_dir)/pyannote/{}.err"
	cat $(work_dir)/pyannote/*.err
	cat $(work_dir)/pyannote/*.time
	cat $(work_dir)/pyannote/*.err | $(python_cmd) sd_benchmark/calc_total_err.py
	cat $(work_dir)/pyannote/*.time | $(python_cmd) sd_benchmark/calc_total_time.py

calc-err/nemo:
	cat $(list) | xargs -n1 -I {} sh -c "$(MAKE) $(work_dir)/nemo/{}.err"
	cat $(work_dir)/nemo/*.err
	cat $(work_dir)/nemo/*.time
	cat $(work_dir)/nemo/*.err | $(python_cmd) sd_benchmark/calc_total_err.py
	cat $(work_dir)/nemo/*.time | $(python_cmd) sd_benchmark/calc_total_time.py

calc-err/nemo2:
	cat $(list) | xargs -n1 -I {} sh -c "$(MAKE) $(work_dir)/nemo2/{}.err"
	cat $(work_dir)/nemo2/*.err
	cat $(work_dir)/nemo2/*.time
	cat $(work_dir)/nemo2/*.err | $(python_cmd) sd_benchmark/calc_total_err.py
	cat $(work_dir)/nemo2/*.time | $(python_cmd) sd_benchmark/calc_total_time.py

calc-err/sd:
	cat $(list) | xargs -n1 -I {} sh -c "$(MAKE) $(work_dir)/sd/{}.err"
	cat $(work_dir)/sd/*.err
	cat $(work_dir)/sd/*.time
	cat $(work_dir)/sd/*.err | $(python_cmd) sd_benchmark/calc_total_err.py
	cat $(work_dir)/sd/*.time | $(python_cmd) sd_benchmark/calc_total_time.py

calc-err/lium:
	cat $(list) | xargs -n1 -I {} sh -c "$(MAKE) $(work_dir)/lium/{}.err $(work_dir)/lium/{}.rttm $(work_dir)/lium/{}.seg"
	cat $(work_dir)/lium/*.err
	cat $(work_dir)/lium/*.time
	cat $(work_dir)/lium/*.err | $(python_cmd) sd_benchmark/calc_total_err.py
	cat $(work_dir)/lium/*.time | $(python_cmd) sd_benchmark/calc_total_time.py

calc-err/kaldi-bbc:
	cat $(list) | xargs -n1 -I {} sh -c "$(MAKE) $(work_dir)/kaldi/{}.err $(work_dir)/kaldi/{}.rttm"
	cat $(work_dir)/kaldi/*.err
	cat $(work_dir)/kaldi/*.time
	cat $(work_dir)/kaldi/*.err | $(python_cmd) sd_benchmark/calc_total_err.py
	cat $(work_dir)/kaldi/*.time | $(python_cmd) sd_benchmark/calc_total_time.py

$(work_dir)/pyannote/%.err: $(work_dir)/pyannote/%.rttm
	$(python_cmd) sd_benchmark/pyannote/der.py --audio $(corpus_dir)/audio/$*.wav --f1 $(corpus_dir)/audio/$*.rttm --f2 $^ --output $@

$(work_dir)/lium/%.err: $(work_dir)/lium/%.rttm
	$(python_cmd) sd_benchmark/pyannote/der.py --audio $(corpus_dir)/audio/$*.wav --f1 $(corpus_dir)/audio/$*.rttm --f2 $^ --output $@

$(work_dir)/nemo/%.err: $(work_dir)/nemo/%.rttm
	$(python_cmd) sd_benchmark/pyannote/der.py --audio $(corpus_dir)/audio/$*.wav --f1 $(corpus_dir)/audio/$*.rttm --f2 $^ --output $@

$(work_dir)/nemo2/%.err: $(work_dir)/nemo2/%.rttm
	$(python_cmd) sd_benchmark/pyannote/der.py --audio $(corpus_dir)/audio/$*.wav --f1 $(corpus_dir)/audio/$*.rttm --f2 $^ --output $@

$(work_dir)/sd/%.err: $(work_dir)/sd/%.rttm
	$(python_cmd) sd_benchmark/pyannote/der.py --audio $(corpus_dir)/audio/$*.wav --f1 $(corpus_dir)/audio/$*.rttm --f2 $^ --output $@
$(work_dir)/kaldi/%.err: $(work_dir)/kaldi/%.rttm
	$(python_cmd) sd_benchmark/pyannote/der.py --audio $(corpus_dir)/audio/$*.wav --f1 $(corpus_dir)/audio/$*.rttm --f2 $^ --output $@

clean:
	rm -rf $(work_dir)/pyannote $(work_dir)/lium $(work_dir)/nemo

.EXPORT_ALL_VARIABLES:	
