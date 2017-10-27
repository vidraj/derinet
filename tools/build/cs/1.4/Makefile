all: derinet-1-4.tsv

derinet-1-4.tsv: derinet-1-3.tsv
	./create-1.4.py > log

derinet-1-3.tsv:
	cp ../../../../data/releases/cs/derinet-1-3.tsv "./$@"
