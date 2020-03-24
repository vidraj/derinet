.PHONY: clean

derinet-2-1.tsv: derinet-2-0.tsv ../../../data-api/derinet2/derinet/modules/cs/recogFW.py
	../../../data-api/derinet2/process_scenario.py \
		Load "$<" \
		cs.AddRootMorphemesFromFile ./prepare-root-segmentations/induced-segmentations.tsv \
		cs.AddLoanwordMarks \
		Save "$@" > log 2>&1

../../../data-api/derinet2/derinet/modules/cs/recogFW.py:  # load tool for recognition of foreign words
	wget -O ../../../data-api/derinet2/derinet/modules/cs/fwrv2.zip https://github.com/lukyjanek/foreign-words-recognition/archive/v2.0.zip
	unzip ../../../data-api/derinet2/derinet/modules/cs/fwrv2.zip -d ../../../data-api/derinet2/derinet/modules/cs/
	mv ../../../data-api/derinet2/derinet/modules/cs/foreign-words-recognition-2.0/recogFW.py ../../../data-api/derinet2/derinet/modules/cs/
	rm -rf ../../../data-api/derinet2/derinet/modules/cs/fwrv2.zip ../../../data-api/derinet2/derinet/modules/cs/foreign-words-recognition-2.0/

derinet-2-0.tsv: ../2.0/derinet-2-0.tsv
	cp -a "$<" "$@"

clean:
	rm -rf ../../../data-api/derinet2/derinet/modules/cs/recogFW.py
# 	rm -f log log-tag-masks derinet-1-7.tsv derinet-1-7-tag-masks.tsv derinet-2-0.tsv
# 	rm -f allomorph-overlap.csv tag-masks.tsv
# 	$(MAKE) -C prepare-root-segmentations clean
