SHELL=/bin/bash

# KOMPLETNÍ RYCHLÉ SPUŠTĚNÍ

# provede vše: extrakci (extrahuje derivace, porovná extrahované s
# DeriNetem a vrátí pouze sirotky s potenciálními rodiči) a data k
# anotaci (jeden soubor se sirotky, pro které je navržen pouze jeden
# potenciální rodič; druhý soubor se sirotky s více navrženými
# potenciálními rodiči)
all: extraction foranotator clean

# provede pouze extrakci
extraction: extract derin compare

# provede pouze vytvoření dat k anotaci
foranotator: onepar morepar anotated

# EXTRAKCE DAT (nutno dodat rozbalený soubor s daty,
# kvůli licenci není součástí)
extract:
	python3 'extraction/extract-wf.py' -s 'ssjc-utf8.xml'

derin:
	git clone 'https://github.com/vidraj/derinet.git'
	cp -r 'derinet/tools/data-api/derinet2/derinet' 'comparison/derinet'
	cp 'derinet/data/releases/cs/derinet-1-5-1.tsv' .

compare:
	mkdir -p 'comparison/ssjc'
	python3 'comparison/compar-ssjc-derinet.py' -s 'ssjc-wf.tsv' -d 'derinet-1-5-1.tsv' -i 'comparison/ssjc/inside.dat' -o 'comparison/ssjc/outside.dat' -c 'comparison/ssjc/composites.dat' -n 'comparison/ssjc/noncomposites.dat' -a 'comparison/ssjc/all-relations.dat'

# VYTVOŘENÍ SOUBORŮ PRO RUČNÍ ANOTOVÁNÍ

# vytvoří soubor obsahující retrográdně seřazené páry k anotaci,
# (tzn. zpracovává pouze ty vztahy, u kterých je navržen pouze
# jeden potenciální rodič
onepar:
	python3 'one-parent.py' 'comparison/ssjc/noncomposites.dat' > '../for-annotation/all-one-parent.tsv'

# vytvoří soubor obsahující seřazená zbylá data k anotaci, tzn. vztahy,
# u kterých je navrženo několik potenciálních rodičů
morepar:
	python3 'more-parents.py' 'comparison/ssjc/noncomposites.dat' > '../for-annotation/all-more-parent.tsv'

# z dat k anotaci se odstraní již anotované relace ve wiktionary
anotated:
	python3 'remove-anotated.py' '../for-annotation/all-one-parent.tsv' '../../2018_04_wiktionary/for-annotation/all-one-parent.tsv' > '../for-annotation/all-one-minus-wikt.tsv'
	python3 'remove-anotated.py' '../for-annotation/all-more-parent.tsv' '../../2018_04_wiktionary/for-annotation/all-more-parent.tsv' > '../for-annotation/all-more-minus-wikt.tsv'

# UVEDENÍ ADRESÁŘE DO PŮVODNÍHO STAVU (ZBYDOU JEN DATA PRO ANOTÁTORA)
clean:
	rm -rf 'derinet'
	rm -rf 'comparison/derinet'
	rm -f 'derinet-1-5-1.tsv'
	rm -f 'ssjc-wf.tsv'
	rm -rf 'comparison/ssjc'
