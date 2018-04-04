najdirozdily:
	./rozdily.pl > nalezene_rozdily.txt

pripony:
	cat nalezene_rozdily.txt | perl -C -pne 's/\S+(\S\S\S\S)/$$1/g;$$_' | sort | uniq -c | sort -nr | head -n20

delsi:
	cat noncomposites.dat | grep -v ';' | perl -C -ne '$$line=$$_;s/_\S+//g;chomp;my($$child,$$parent)=split;print $$line if length($$parent) > length($$child)' > delsi_rodic.txt
