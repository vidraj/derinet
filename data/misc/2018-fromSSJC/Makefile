najdirozdily:
	./rozdily.pl > nalezene_rozdily.txt

pripony:
	cat nalezene_rozdily.txt | perl -C -pne 's/\S+(\S\S\S\S)/$$1/g;$$_' | sort | uniq -c | sort -nr | head -n20
