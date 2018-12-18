SHELL=/bin/bash

all: convert extractU extractC processU processC

convert:
	for i in *'.xlsx'; do \
		xlsx2csv -i $$i > $$i'.csv'; \
		cat $$i'.csv' | grep -v 'ZÁKLADOVÉ,ODVOZENÉ' | sed -e 's/pro sloupec A//g' -e 's/PRÁZDNO,navržený vztah v pořádku//g' -e 's/§,opačně//g' -e 's/\\,mezi B a C neexistuje přímý derivační vztah//g' -e 's/@,"na hranici příbuznosti, zastřená motivace \/ lidová, nejasná etymologie \/ doložený vznik je v rozporu s intuitivním odvozením a podobné nejasnosti..."//g' -e 's/?,nedovedu posoudit \/ nechci řešit \/\/ v kombinaci s jiným znakem vyjadřuje prostě nejistotu :)//g' -e 's/!,upozornění na homonymii (minimálně) jednoho ze slov//g' -e 's/],nesedí slovní druh//g' -e 's/"pro sloupce D, E:"//g' -e 's/*,určitě značkové//g' -e 's/lexém,určitě odvozené a znám ZS//g' -e 's/"""","neznám ZS nebo vůbec nechci řešit, jestli je odvozené nebo značkové"//g' -e 's/,ZNAČKA,VÝZNAM//g' -e 's/§,přímý derivační vztah (C odvozeno od B)//g' -e 's/!,homonymie//g' -e 's/(,derivát je kompozitum//g' -e 's/?,nejasný případ \/ nevím//g' | grep -v '^,,,,,' > $$i'.csv2'; \
		cat $$i'.csv2' | sed -e 's/,/\t/g' -e 's/""""/"/g' | tr -d ' ' > $$i'.tsv'; \
		rm $$i'.csv' $$i'.csv2'; \
	done

extractU:
	for i in 'deriv'*'.tsv'; do \
		cat $$i | grep '\*' >> 'extracted-unmotivated.tsv'; \
	done

processU:
	echo '# one-column list of unmotivated lemmas' > 'all-unmotivated.txt'
	cat 'extracted-unmotivated.tsv' | python3 'tools/listUnmotivated.py' | sort | uniq | sed '1d' | python3 'tools/checkUnmotivated.py' >> 'all-unmotivated.txt'

extractC:
	for i in 'deriv'*'.tsv'; do \
		cat $$i | grep '\+' >> 'extracted-compounds-1.tsv'; \
	done
	for i in 'more'*'.tsv'; do \
		cat $$i | grep '(' >> 'extracted-compounds-2.tsv'; \
	done

processC:
	echo '# two-columns list of compounds: lemma \tab compound_segmantation' > 'all-compounds-1.tsv'
	cat 'extracted-compounds-1.tsv' | python3 'tools/listCompounds.py' >> 'all-compounds-1.tsv'
	echo '# two-columns list of compounds (one of them [or both] is compound): lemma \tab lemma' > 'all-compounds-2.tsv'
	cat 'extracted-compounds-2.tsv' | python3 'tools/listCompounds.py' >> 'all-compounds-2.tsv'

clean:
	rm *'.tsv' *.'txt'
