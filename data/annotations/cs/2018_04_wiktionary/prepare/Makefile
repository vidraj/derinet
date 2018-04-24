SHELL=/bin/bash

# KOMPLETNÍ RYCHLÉ SPUŠTĚNÍ

# provede vše: extrakci (stáhne jazykové mutace wiktionary, extrahuje
# z nich derivace, porovná extrahované s DeriNetem a vrátí
# pouze sirotky s potenciálními rodiči) a data k anotaci (jeden soubor
# se sirotky, pro které je navržen pouze jeden potenciální rodič;
# druhý soubor se sirotky s více navrženými potenciálními rodiči)
all: extraction foreanotator clean

# provede pouze extrakci
extraction: download cswikt enwikt frwikt dewikt plwikt mergewikt

# provede pouze vytvoření dat k anotaci
foranotator: onepar anotated morepar

# EXTRAKCE DAT Z WIKTIONARY

# stáhne mutace wiktionary a derinetí API
download:
	wget 'https://dumps.wikimedia.org/cswiktionary/20180120/cswiktionary-20180120-pages-articles-multistream.xml.bz2' -P 'extraction/'
	wget 'https://dumps.wikimedia.org/enwiktionary/20180120/enwiktionary-20180120-pages-articles-multistream.xml.bz2' -P 'extraction/'
	wget 'https://dumps.wikimedia.org/dewiktionary/20180201/dewiktionary-20180201-pages-articles-multistream.xml.bz2' -P 'extraction/'
	wget 'https://dumps.wikimedia.org/frwiktionary/20180201/frwiktionary-20180201-pages-articles-multistream.xml.bz2' -P 'extraction/'
	wget 'https://dumps.wikimedia.org/plwiktionary/20180201/plwiktionary-20180201-pages-articles-multistream.xml.bz2' -P 'extraction/'
	git clone 'https://github.com/vidraj/derinet.git'
	cp -r 'derinet/tools/data-api/derinet2/derinet' 'comparison/derinet'
	cp 'derinet/data/releases/cs/derinet-1-5-1.tsv' 'comparison/'
	rm -rf derinet

# extrahuje derivace z české mutace a porovná je s DeriNetem
cswikt:
	python3 'extraction/wiktionary.py' -d 'extraction/cswiktionary-20180120-pages-articles-multistream.xml.bz2' -l 'cs' -o 'extraction/cs.wkt'
	mkdir -p 'comparison/cs/'
	python3 'comparison/comparison.py' -w 'extraction/cs.wkt' -d 'comparison/derinet-1-5-1.tsv' -i 'comparison/cs/inside.dat' -o 'comparison/cs/outside.dat' -c 'comparison/cs/composites.dat' -n 'comparison/cs/noncomposites.dat' -a 'comparison/cs/all-relations.dat'

# extrahuje derivace z anglické mutace a porovná je s DeriNetem
enwikt:
	python3 'extraction/wiktionary.py' -d 'extraction/enwiktionary-20180120-pages-articles-multistream.xml.bz2' -l 'ze' -o 'extraction/en.wkt'
	mkdir -p 'comparison/en/'
	python3 'comparison/comparison.py' -w 'extraction/en.wkt' -d 'comparison/derinet-1-5-1.tsv' -i 'comparison/en/inside.dat' -o 'comparison/en/outside.dat' -c 'comparison/en/composites.dat' -n 'comparison/en/noncomposites.dat' -a 'comparison/en/all-relations.dat'

# extrahuje derivace z francouzské mutace a porovná je s DeriNetem
frwikt:
	python3 'extraction/wiktionary.py' -d 'extraction/frwiktionary-20180120-pages-articles-multistream.xml.bz2' -l 'zf' -o 'extraction/fr.wkt'
	mkdir -p 'comparison/fr/'
	python3 'comparison/comparison.py' -w 'extraction/fr.wkt' -d 'comparison/derinet-1-5-1.tsv' -i 'comparison/fr/inside.dat' -o 'comparison/fr/outside.dat' -c 'comparison/fr/composites.dat' -n 'comparison/fr/noncomposites.dat' -a 'comparison/fr/all-relations.dat'

# extrahuje derivace z německé mutace a porovná je s DeriNetem
dewikt:
	python3 'extraction/wiktionary.py' -d 'extraction/dewiktionary-20180120-pages-articles-multistream.xml.bz2' -l 'zd' -o 'extraction/de.wkt'
	mkdir -p 'comparison/de/'
	python3 'comparison/comparison.py' -w 'extraction/de.wkt' -d 'comparison/derinet-1-5-1.tsv' -i 'comparison/de/inside.dat' -o 'comparison/de/outside.dat' -c 'comparison/de/composites.dat' -n 'comparison/de/noncomposites.dat' -a 'comparison/de/all-relations.dat'

# extrahuje derivace z polské mutace a porovná je s DeriNetem
plwikt:
	python3 'extraction/wiktionary.py' -d 'extraction/plwiktionary-20180120-pages-articles-multistream.xml.bz2' -l 'zp' -o 'extraction/pl.wkt'
	mkdir -p 'comparison/pl/'
	python3 'comparison/comparison.py' -w 'extraction/pl.wkt' -d 'comparison/derinet-1-5-1.tsv' -i 'comparison/pl/inside.dat' -o 'comparison/pl/outside.dat' -c 'comparison/pl/composites.dat' -n 'comparison/pl/noncomposites.dat' -a 'comparison/pl/all-relations.dat'

# sloučí extrahované derivace siroků a jejich potenciálních rodičů
# ze všech jazykových mutací do jednoho souboru:
# jeden soubor kompozit; druhý nekompozit; třetí lexémů, které v
# DeriNetu nejsou
mergewikt:
	python3 'comparison/merge-relations.py' -m 'comparison/cs/composites.dat,comparison/en/composites.dat,comparison/de/composites.dat,comparison/fr/composites.dat,comparison/pl/composites.dat' -o 'comparison/merged-composites.dat'
	python3 'comparison/merge-relations.py' -m 'comparison/cs/noncomposites.dat,comparison/en/noncomposites.dat,comparison/de/noncomposites.dat,comparison/fr/noncomposites.dat,comparison/pl/noncomposites.dat' -o 'comparison/merged-noncomposites.dat'
	python3 'comparison/merge-outside.py' -m 'comparison/cs/outside.dat,comparison/de/outside.dat,comparison/en/outside.dat,comparison/fr/outside.dat,comparison/pl/outside.dat' -o 'comparison/merged-outside.dat'

# VYTVOŘENÍ SOUBORŮ PRO RUČNÍ ANOTOVÁNÍ

# vytvoří soubor obsahující retrográdně seřazené páry k anotaci,
# (tzn. zpracovává pouze ty vztahy, u kterých je navržen pouze
# jeden potenciální rodič
onepar:
	python3 one-parent.py 'comparison/merged-noncomposites.dat' > '../for-annotation/all-one-parent.tsv'

# vytvoří soubor obsahující seřazená zbylá data k anotaci, tzn. vztahy,
# u kterých je navrženo několik potenciálních rodičů
morepar:
	python3 more-parents.py 'comparison/merged-noncomposites.dat' > '../for-annotation/all-more-parent.tsv'

# ze souboru se všemi páry k anotaci odebere již oanotované páry,
# a vytvoří tím soubor se zbývajícími páry k anotaci (použito pro
# odstranění oanotovaných testovacích dat, která byla zaslána mnohem
# dříve než dávka 'onepar').
anotated:
	python3 remove-anotated.py '../for-annotation/all-one-parent.tsv' '../for-annotation/anotator-testing.tsv' > '../for-annotation/all-one-minus-testing.tsv'

# UVEDENÍ ADRESÁŘE DO PŮVODNÍHO STAVU (ZBYDOU JEN DATA PRO ANOTÁTORA)
clean:
	rm -rf 'extraction/patterns/__pycache__'
	rm -rf 'extraction/__pycache__'
	rm -rf 'comparison/__pycache__'
	rm -f extraction/*.xml.bz2
	rm -f extraction/*.wkt
	rm -rf 'comparison/derinet'
	rm -f 'comparison/derinet-1-5-1.tsv'
	rm -rf 'comparison/cs'
	rm -rf 'comparison/en'
	rm -rf 'comparison/fr'
	rm -rf 'comparison/pl'
	rm -rf 'comparison/de'
	rm -f comparison/*.dat
