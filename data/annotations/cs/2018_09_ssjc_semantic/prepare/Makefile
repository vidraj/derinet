SHELL=/bin/bash

DERINET='../../../../releases/cs/derinet-1-7.tsv'

all: data preprocess install mlexperiments mlprocess mleval done

# individual steps
data: SSJC MORFFLEXCZ PMC VALLEX DERINET Multiple
preprocess: MergeAnnotations NEGATIVES AddFeatures CorrectFeatures
install: py3env/
mlexperiments: Experiments
mlprocess: PrepareForPrediction Predict ApplyTreshold MakeAnnotationFile
mleval: PrepareForEvaluation Evaluate
done: clean

# DATA EXTRACTION AND PREPROCESSING

# extraction of semantic labels from SSJČ, automatic annotation
SSJC: ../for-annotation/semantic-labels-ssjc.tsv
	@echo 'Extraction and annotation from SSJC complete. See file: ../for-annotation/semantic-labels-ssjc.tsv'
	@echo 'WARNING: BE CAREFUL, DATA CAN CONTAIN MANUAL ANNOTATIONS!'

../for-annotation/semantic-labels-ssjc.tsv: ssjc-utf8.xml
	python3 'extract-ssjc.py' 'ssjc-utf8.xml' $(DERINET) > '../for-annotation/potentials-ssjc.tsv'
	python3 'annotate.py' '../for-annotation/potentials-ssjc.tsv' $(DERINET) > '../for-annotation/semantic-labels-ssjc.tsv'
	rm -f '../for-annotation/potentials-ssjc.tsv'

ssjc-utf8.xml:
	@echo -e 'You need SSJČ .xml data.'


# extraction of semantic labels from MorfFlexCZ, automatic annotation
MORFFLEXCZ: ../for-annotation/semantic-labels-morfflex.tsv
	@echo 'Extraction and annotation from MorfFlexCZ completed. See file: ../for-annotation/semantic-labels-morfflex.tsv'
	@echo 'WARNING: BE CAREFUL, DATA CAN CONTAIN MANUAL ANNOTATIONS!'

../for-annotation/semantic-labels-morfflex.tsv:
	python3 'extract-morfflex.py' $(DERINET) > '../for-annotation/potentials-morfflex.tsv'
	python3 'annotate.py' '../for-annotation/potentials-morfflex.tsv' $(DERINET) > '../for-annotation/semantic-labels-morfflex.tsv'
	rm -f '../for-annotation/potentials-morfflex.tsv'


# extraction of semantic labels from PMČ, need manual annotation
PMC: ../for-annotation/semantic-labels-pmc.tsv
	@echo 'Extraction and annotation from PMC completed. See file: ../for-annotation/semantic-labels-pcm.tsv'
	@echo 'WARNING: BE CAREFUL, DATA CAN CONTAIN MANUAL ANNOTATIONS!'

../for-annotation/semantic-labels-pmc.tsv:
	python3 'extract-pmc.py' $(DERINET) > '../for-annotation/semantic-labels-pmc.tsv'


# extraction of semantic labels from VALLEX, automatic annotation
VALLEX: ../for-annotation/semantic-labels-vallex.tsv
	@echo 'Extraction and annotation from VALLEX3 completed. See file: ../for-annotation/semantic-labels-vallex.tsv'
	@echo 'WARNING: BE CAREFUL, DATA CAN CONTAIN MANUAL ANNOTATIONS!'

../for-annotation/semantic-labels-vallex.tsv: vallex_3.0.xml
	python3 'extract-vallex.py' 'vallex_3.0.xml' > '../for-annotation/potentials-vallex.tsv'
	python3 'annotate.py' '../for-annotation/potentials-vallex.tsv' $(DERINET) > '../for-annotation/semantic-labels-vallex.tsv'
	rm -f '../for-annotation/potentials-vallex.tsv'

vallex_3.0.xml:
	@echo 'You need vallex_3.0.xml dictionary from LINDAT/CLARIN (http://hdl.handle.net/11234/1-2307).'


# check relations with more than one semantic labels
Multiple: ../for-annotation/semantic-labels-ssjc.tsv ../for-annotation/semantic-labels-morfflex.tsv ../for-annotation/semantic-labels-pmc.tsv
	cat '../for-annotation/semantic-labels-ssjc.tsv' | sed '1d' | grep -e '^%' | cut -d $$'\t' -f 2,3,4 | python3 'multiple-labels.py' > '../for-annotation/multiple-labeled-ssjc.tsv'
	cat '../for-annotation/semantic-labels-morfflex.tsv' | sed '1d' | grep -e '^%' | cut -d $$'\t' -f 2,3,4 | python3 'multiple-labels.py' > '../for-annotation/multiple-labeled-morfflex.tsv'
	cat '../for-annotation/semantic-labels-pmc.tsv' | sed '1d' | grep -e '^%' | cut -d $$'\t' -f 2,3,4 | python3 'multiple-labels.py' > '../for-annotation/multiple-labeled-pmc.tsv'
	cat '../for-annotation/semantic-labels-vallex.tsv' | sed '1d' | grep -e '^%' | cut -d $$'\t' -f 2,3,4 | python3 'multiple-labels.py' > '../for-annotation/multiple-labeled-vallex.tsv'


# merge all extracted data to one file and check wheather there are relations with more labels
MergeAnnotations: ../for-annotation/semantic-labels.tsv
	@echo 'Merging of annotated files completed. See file: ../for-annotation/semantic-labels.tsv'
	@echo 'WARNING: BE CAREFUL, DATA CAN CONTAIN MANUAL ANNOTATIONS!'

../for-annotation/semantic-labels.tsv: ../for-annotation/semantic-labels-ssjc.tsv ../for-annotation/semantic-labels-morfflex.tsv ../for-annotation/semantic-labels-pmc.tsv
	cat '../for-annotation/semantic-labels-ssjc.tsv' | grep $$'^\%' >> '../for-annotation/semantic-labels-1.tsv'
	cat '../for-annotation/semantic-labels-morfflex.tsv' | grep $$'^\%' >> '../for-annotation/semantic-labels-1.tsv'
	cat '../for-annotation/semantic-labels-pmc.tsv' | grep $$'^\%' >> '../for-annotation/semantic-labels-1.tsv'
	cat '../for-annotation/semantic-labels-vallex.tsv' | grep $$'^\%' >> '../for-annotation/semantic-labels-1.tsv'
	cat '../for-annotation/semantic-labels-1.tsv' | sed -e 's/\r//g' | sort | uniq > '../for-annotation/semantic-labels.tsv'
	cat '../for-annotation/semantic-labels.tsv' | cut -d $$'\t' -f 2,3,4 | python3 'multiple-labels.py' > '../for-annotation/multiple-labeled-all.tsv'
	rm -f '../for-annotation/semantic-labels-1.tsv'


# extraction of semantic labels (NONE) from DeriNet, manual annotation
NEGATIVES: ../for-annotation/negatives-derinet.tsv
	@echo 'Extraction from DeriNet completed. See file: ../for-annotation/negatives-derinet.tsv'
	@echo 'WARNING: BE CAREFUL, DATA CAN CONTAIN MANUAL ANNOTATIONS!'

../for-annotation/negatives-derinet.tsv: ../for-annotation/semantic-labels.tsv
	python3 'extract-derinet.py' $(DERINET) > '../for-annotation/non-labeled-derinet.tsv'
	cat '../for-annotation/semantic-labels.tsv' | grep -v $$'\tpodst\.' | grep -v $$'\tzpodst\.' | cut -f 2,3,4,5 > '../for-annotation/labeled-data.tsv'
	python3 'add-negatives.py' '../for-annotation/labeled-data.tsv' '../for-annotation/non-labeled-derinet.tsv' > '../for-annotation/negatives-derinet.tsv'
	rm -f '../for-annotation/non-labeled-derinet.tsv' '../for-annotation/labeled-data.tsv'


# merge extracted positive and negative examples, automaticaly add features from MorphoDiTa, SYN2015 and VALLEX
AddFeatures: ../for-annotation/MLdata-semantic-labels.tsv
	@echo 'Adding of features completed. See file: ../for-annotation/MLdata-semantic-labels.tsv'

../for-annotation/MLdata-semantic-labels.tsv: ../for-annotation/semantic-labels.tsv ../for-annotation/negatives-derinet.tsv word-list-syn2015.tsv word-list-vallex.tsv
	cat '../for-annotation/semantic-labels.tsv' | grep -v $$'\tpodst\.' | grep -v $$'\tzpodst\.' | cut -f 2,3,4,5 > 'training-data.tsv'
	cat '../for-annotation/negatives-derinet.tsv' | grep $$'^\%' | cut -f 2,3,4 >> 'training-data.tsv'
	cat 'training-data.tsv' | cut -d $$'\t' -f 1,2 | sed -e 's/–[A-Z]*//g' | sed -e 's/\t/\n/g' | sort | uniq > 'for-analyze.txt'
	curl -F 'data=@for-analyze.txt' -F 'output=json' -F 'input=vertical' http://lindat.mff.cuni.cz/services/morphodita/api/tag > 'word-list-morphodita.json'
	python3 'add-features.py' 'training-data.tsv' 'word-list-syn2015.tsv' 'word-list-morphodita.json' 'word-list-vallex.tsv' > '../for-annotation/MLdata-semantic-labels.tsv'
	rm -f 'training-data.tsv' 'for-analyze.txt' 'word-list-morphodita.json'

word-list-syn2015.tsv: syn2015.gz
	zgrep -v '^<' 'syn2015.gz' | cut -d $$'\t' -f 1,2,3 | sort | uniq -c | sort -nr > 'word-list-syn2015.tsv'

word-list-vallex.tsv: vallex_3.0.xml
	cat 'vallex_3.0.xml' | grep -o $$'\<mlemma.*' | sed -e 's/>/ /g' -e 's/<\/mlemma//g' | grep -e $$'aspect' | awk '{print $$NF " " $$2}' | grep -v $$'"iter"' | sed -e 's/aspect="impf"/I/g' -e 's/aspect="pf"/P/g' -e 's/aspect="biasp"/B/g' | sort | uniq > word-list-vallex.tsv

syn2015.gz:
	@echo 'You need syn2015.gz corpus from Czech National Corpus Institution.'


# fix some incorrect features
CorrectFeatures: ../for-annotation/MLdata-semantic-labels.tsv ../for-annotation/feature-corrections.tsv
	python3 'correct-features.py' '../for-annotation/MLdata-semantic-labels.tsv' '../for-annotation/feature-corrections.tsv' > '../hand-annotated/MLSemLab.tsv'
	rm -f '../for-annotation/MLdata-semantic-labels.tsv'
	@echo 'Data was corrected. It is prepared for Machine Learning experiments. Date is placed in: ../hand-annotated/MLSemLab.tsv'


# INSTALLATION OF VIRTUAL ENVIRONMENT FOR MACHINE LEARNING

py3env/:
	virtualenv -p /usr/bin/python3 py3env
	@( \
	source py3env/bin/activate; \
	pip3 install pandas; \
	pip3 install numpy; \
	pip3 install scikit-learn; \
	pip3 install scipy; \
	pip3 install graphviz; \
	)


# MACHINE LEARNING

# various experiments (before training final models)
Experiments: py3env/ ../hand-annotated/MLSemLab.tsv
	py3env/bin/python3 'ml-experiments.py' '../hand-annotated/MLSemLab.tsv' > '../hand-annotated/ml-exp-results.txt'
	rm -f '../hand-annotated/SemLab-DTree-experiment'


# extraction of data for prediction from DeriNet
PrepareForPrediction: ../hand-annotated/for-prediction.tsv
	@echo 'Data for prediction (from DeriNet) was prepared. It is prepared for labeling by Machine Learning. Date is placed in: ../hand-annotated/for-prediction.tsv'

../hand-annotated/for-prediction.tsv: word-list-syn2015.tsv word-list-vallex.tsv
	python3 'ml-for-prediction.py' $(DERINET) | cut -d $$'\t' -f 1,2 | sed -e 's/–[A-Z]*//g' | sed -e 's/\t/\n/g' | sort | uniq > 'for-analyze.txt'
	split -l 75000 'for-analyze.txt'
	curl -F 'data=@xaa' -F 'output=json' -F 'input=vertical' http://lindat.mff.cuni.cz/services/morphodita/api/tag > 'word-list-morphodita1.json'
	curl -F 'data=@xab' -F 'output=json' -F 'input=vertical' http://lindat.mff.cuni.cz/services/morphodita/api/tag > 'word-list-morphodita2.json'
	curl -F 'data=@xac' -F 'output=json' -F 'input=vertical' http://lindat.mff.cuni.cz/services/morphodita/api/tag > 'word-list-morphodita3.json'
	curl -F 'data=@xad' -F 'output=json' -F 'input=vertical' http://lindat.mff.cuni.cz/services/morphodita/api/tag > 'word-list-morphodita4.json'
	curl -F 'data=@xae' -F 'output=json' -F 'input=vertical' http://lindat.mff.cuni.cz/services/morphodita/api/tag > 'word-list-morphodita5.json'
	python3 'ml-for-prediction.py' $(DERINET) | python3 'add-features.py' '@stdin' 'word-list-syn2015.tsv' 'word-list-morphodita1.json|word-list-morphodita2.json|word-list-morphodita3.json|word-list-morphodita4.json|word-list-morphodita5.json' 'word-list-vallex.tsv' > '../hand-annotated/for-prediction.tsv'
	rm -f 'for-analyze.txt' 'xaa' 'xab' 'xac' 'xad' 'xae' 'word-list-morphodita1.json' 'word-list-morphodita2.json' 'word-list-morphodita3.json' 'word-list-morphodita4.json' 'word-list-morphodita5.json'


# train models for prediction and predict given data
Predict: ../hand-annotated/predicted.tsv
	@echo 'Unkwnon relations were predicted. See ../hand-annotated/predicted.tsv.'
	@echo 'Various tresholds were tested. See ../hand-annotated/evaluation-test-devel-train.txt'

../hand-annotated/predicted.tsv: ../hand-annotated/for-prediction.tsv
	py3env/bin/python3 'ml-predict.py' '../hand-annotated/MLSemLab.tsv' '../hand-annotated/for-prediction.tsv' '../hand-annotated/predicted.tsv' > '../hand-annotated/evaluation-test-devel-train.txt'
	rm -f '../hand-annotated/SemLab-DTree'


# apply choosen treshold
ApplyTreshold: ../hand-annotated/predicted-with-treshold.tsv
	@echo 'Tresholds were applied. Predicted data saved: ../hand-annotated/predicted-with-treshold.tsv'

../hand-annotated/predicted-with-treshold.tsv: ../hand-annotated/predicted.tsv
	python3 'ml-apply-treshold.py' '../hand-annotated/predicted.tsv' 'DIMINUTIVE:0.75|FEMALE:0.4|POSSESSIVE:0.4|ASPECT:0.4|ITERATIVE:0.5|NONE:0.0' > '../hand-annotated/predicted-with-treshold.tsv'


# prepare data for final evaluation of models (for manual annotation)
PrepareForEvaluation: ../hand-annotated/evaluation-data.tsv
	@echo 'Data for evaluation (manual annotation) was prepared. See ../hand-annotated/evaluation-data.tsv'
	@echo 'WARNING: BE CAREFUL, DATA CAN CONTAIN MANUAL ANNOTATIONS!'

../hand-annotated/evaluation-data.tsv: ../hand-annotated/predicted-with-treshold.tsv
	python3 'ml-for-evaluation.py' '../hand-annotated/predicted-with-treshold.tsv' > '../hand-annotated/evaluation-data.tsv'


# measure evaluation metrics for manualy annotated data
Evaluate: ../hand-annotated/evaluation-results.txt
	@echo 'Evaluation done. Results are saved here: ../hand-annotated/evaluation-results.txt'

../hand-annotated/evaluation-results.txt: ../hand-annotated/evaluation-data.tsv
	py3env/bin/python3 'ml-evaluate.py' '../hand-annotated/evaluation-data.tsv' > '../hand-annotated/evaluation-results.txt'


# create anonation file of semnatic labels (parent \t child \t label \t probability),
# only those relations with higher probbility than given tresholds
# these relations will be released in DeriNet database
MakeAnnotationFile: ../hand-annotated/final-semantic-labels.tsv
	@echo 'Annotation file created and saved. See ../hand-annotated/final-semantic-labels.tsv'
	@echo 'WARNING: BE CAREFUL, DATA CAN CONTAIN MANUAL ANNOTATIONS!'

../hand-annotated/final-semantic-labels.tsv: ../hand-annotated/predicted-with-treshold.tsv
	cat '../hand-annotated/predicted-with-treshold.tsv' | grep -v $$'NONE' | sed -e 's/|/\t/g' > '../hand-annotated/final-semantic-labels.tsv'
	rm -f '../hand-annotated/predicted-with-treshold.tsv' '../hand-annotated/for-prediction.tsv' '../hand-annotated/predicted.tsv'


# clean project folders
clean:
	rm -f 'word-list-syn2015.tsv' 'word-list-vallex.tsv' 'training-data.tsv' 'for-analyze.txt' 'word-list-morphodita.json'
	rm -f '../hand-annotated/predicted-with-treshold.tsv' '../hand-annotated/for-prediction.tsv' '../hand-annotated/predicted.tsv'
	rm -f '../for-annotation/potentials-ssjc.tsv' '../for-annotation/potentials-morfflex.tsv' '../for-annotation/potentials-vallex.tsv'
	rm -f '../for-annotation/semantic-labels-1.tsv' '../for-annotation/non-labeled-derinet.tsv' '../for-annotation/labeled-data.tsv'
	rm -f '../for-annotation/MLdata-semantic-labels.tsv' '../hand-annotated/SemLab-DTree-experiment' '../hand-annotated/SemLab-DTree-experiment.pdf'
	rm -f 'for-analyze.txt' 'xaa' 'xab' 'xac' 'xad' 'xae' 'word-list-morphodita1.json' 'word-list-morphodita2.json' 'word-list-morphodita3.json'
	rm -f 'word-list-morphodita4.json' 'word-list-morphodita5.json' '../hand-annotated/SemLab-DTree' '../hand-annotated/SemLab-DTree.pdf'
	rm -rf 'py3env/'


# MANUAL POSTPROCESSING
possessives_female: ../hand-annotated/final-correction-fix.tsv
	@echo 'WARNING: BE CAREFUL, DATA CAN CONTAIN MANUAL ANNOTATIONS!'

../hand-annotated/final-correction-fix.tsv: ../hand-annotated/final-semantic-labels.tsv 
	python3 'poses-check.py' $(DERINET) '../hand-annotated/final-semantic-labels.tsv' '../hand-annotated/final-correction-fix.tsv' '../hand-annotated/final-correction-add.tsv'
	python3 'female-check.py' $(DERINET) '../hand-annotated/final-semantic-labels.tsv' >> '../hand-annotated/final-correction-add.tsv'
