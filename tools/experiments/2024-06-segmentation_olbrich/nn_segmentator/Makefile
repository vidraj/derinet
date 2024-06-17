# .PHONY: download_all

SHELL = bash

run:
	python3 main.py

 tensorboard_log:
		tensorboard --logdir logs

send_to_cluster:
	scp -r ./*    olbrich@geri.ms.mff.cuni.cz:~/personal_work_ms/nn_segmentator/

send_nn_to_cluster:
	scp ./mlp_segmentation/conv_segmentator_one_hot.py    olbrich@geri.ms.mff.cuni.cz:~/personal_work_ms/nn_segmentator/mlp_segmentation

evaluate_sigmorphon:
	python3 evaluation/evaluate.py --gold data_sources/sigmorphon/ces.word.test.gold.tsv --guess results/sigmorphon_predictions.txt