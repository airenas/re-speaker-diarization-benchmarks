log?=INFO
python_cmd=PYTHONPATH=./ LOG_LEVEL=$(log) python
############################################################
work_dir=./work
audio_data=./data/WAV16.ZIP
textgrid_data=./data/GRID-SPK.ZIP

$(work_dir)/.done/ $(work_dir)/audio $(work_dir)/grids $(work_dir)/rrtm:
	mkdir -p $@

$(work_dir)/.done/.audio: $(audio_data) | $(work_dir)/.done/ $(work_dir)/audio
	unzip $^ -d $(work_dir)/audio
	touch $@

$(work_dir)/.done/.grids: $(textgrid_data) | $(work_dir)/.done/ $(work_dir)/grids
	unzip $^ -d $(work_dir)/grids
	touch $@

$(work_dir)/.done/.rrtm: $(work_dir)/.done/.grids $(work_dir)/.done/.audio | $(work_dir)/rrtm
	find $(work_dir)/grids -type f -name "*.TextGrid" -print0 | xargs -0 -I {} sh -c "$(python_cmd) sd_benchmark/tg_to_rrtm.py --input {} --out_dir $(work_dir)/audio --prefix $(work_dir)/grids"

	# touch $@

prepare/data: $(work_dir)/.done/.audio $(work_dir)/.done/.rrtm

clean:
	rm -rf $(work_dir)