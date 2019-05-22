.PHONY: clean

CORRECTIONS=final-correction-add.tsv final-correction-fix.tsv

final-semantic-labels-fixed.tsv: final-semantic-labels.tsv correct-annotation.py $(CORRECTIONS)
	./correct-annotation.py $(CORRECTIONS) < "$<" > "$@"

clean:
	rm -f final-semantic-labels-fixed.tsv
