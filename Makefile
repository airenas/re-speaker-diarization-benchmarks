include Makefile.options
log?=INFO
python_cmd=PYTHONPATH=./ LOG_LEVEL=$(log) python
CUDA=cuda:0
list=./work/min.list
############################################################
corpus_dir=./corpus
work_dir=./work
audio_data=./data/WAV16.ZIP
textgrid_data=./data/GRID-SPK.ZIP

$(corpus_dir)/.done/ $(corpus_dir)/audio $(corpus_dir)/grids $(work_dir)/rrtm corpus $(work_dir)/pyannote $(work_dir)/lium \
	$(work_dir)/.done/:
	mkdir -p $@

$(corpus_dir)/.done/.audio: $(audio_data) | $(corpus_dir)/.done/ $(corpus_dir)/audio
	unzip $^ -d $(corpus_dir)/audio
	find $(corpus_dir)/audio -type f -name "*.wav" -print0 | xargs -0 -I {} sh -c "mv {} $(corpus_dir)/audio/"
	touch $@

$(corpus_dir)/.done/.grids: $(textgrid_data) | $(corpus_dir)/.done/ $(corpus_dir)/grids
	unzip $^ -d $(corpus_dir)/grids
	find $(corpus_dir)/grids -type f -name "*.TextGrid" -print0 | xargs -0 -I {} sh -c "mv {} $(corpus_dir)/grids/"
	touch $@

$(corpus_dir)/.done/.rrtm: $(corpus_dir)/.done/.grids $(corpus_dir)/.done/.audio
	find $(corpus_dir)/grids -type f -name "*.TextGrid" -print0 | xargs -0 -I {} sh -c "$(python_cmd) sd_benchmark/tg_to_rrtm.py --input {} --out_dir $(corpus_dir)/audio --prefix $(corpus_dir)/grids"
	touch $@

prepare/data: $(corpus_dir)/.done/.audio $(corpus_dir)/.done/.rrtm

prepare/list: 
	@find $(corpus_dir)/audio -type f -name "*.wav" | xargs -n1 -I {} basename {} .wav | sort

diarization/pyannote:
	cat $(list) | xargs -n1 -I {} sh -c "$(MAKE) $(work_dir)/pyannote/{}.rrtm"

diarization/lium:
	cat $(list) | xargs -n1 -I {} sh -c "$(MAKE) $(work_dir)/lium/{}.rrtm $(work_dir)/lium/{}.seg"

$(work_dir)/.done/.lium-docker: | $(work_dir)/.done/
	cd lium && $(MAKE) dbuild
	touch $@

$(work_dir)/pyannote/%.rrtm: | $(work_dir)/pyannote
	$(python_cmd) sd_benchmark/pyannote/diarization.py --input $(corpus_dir)/audio/$*.wav --output_dir $(work_dir)/pyannote

$(work_dir)/lium/%.seg: $(work_dir)/.done/.lium-docker | $(work_dir)/lium
	docker run --rm -v $$(pwd)/$(corpus_dir)/audio:/in -v $$(pwd)/$(work_dir)/lium:/res airenas/lium:0.1.0 ./run.sh /in/$*.wav /res/$*.seg

$(work_dir)/lium/%.rrtm: $(work_dir)/lium/%.seg | $(work_dir)/lium
	$(python_cmd) sd_benchmark/seg_to_rrtm.py --input $(work_dir)/lium/$*.seg --output $(work_dir)/lium/$*.rrtm

calc-err/pyannote:
	cat $(list) | xargs -n1 -I {} sh -c "$(MAKE) $(work_dir)/pyannote/{}.err"
	cat $(work_dir)/pyannote/*.err
	cat $(work_dir)/pyannote/*.time

calc-err/lium:
	cat $(list) | xargs -n1 -I {} sh -c "$(MAKE) $(work_dir)/lium/{}.err"
	cat $(work_dir)/lium/*.err

$(work_dir)/pyannote/%.err: $(work_dir)/pyannote/%.rrtm
	$(python_cmd) sd_benchmark/pyannote/der.py --f1 $(corpus_dir)/audio/$*.rrtm --f2 $^ --output $@

$(work_dir)/lium/%.err: $(work_dir)/lium/%.rrtm
	$(python_cmd) sd_benchmark/pyannote/der.py --f1 $(corpus_dir)/audio/$*.rrtm --f2 $^ --output $@

clean:
	rm -rf $(work_dir)/pyannote

.EXPORT_ALL_VARIABLES:	
