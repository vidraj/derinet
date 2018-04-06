SHELL=/bin/bash

# vytvoří soubor obsahující retrográdně seřazené páry k anotaci,
# (tzn. zpracovává pouze ty vztahy, u kterých je navržen pouze
# jeden potenciální rodič
pairs:
	python3 create-anotating-list.py '../../../misc/2018-fromWiktionary/merged-noncomposites.dat' > 'all-pairs.tsv'

# vytvoří soubor obsahující (ještě nevím jak) seřazená zbylá data
# k anotaci, tzn. vztahy, u kterých je navrženo několik potenciálních
# rodičů
nonpairs:
	python3

# ze souboru se všemi páry k anotaci odebere již oanotované páry,
# a vytvoří tím soubor se zbývajícími páry k anotaci (použito pro
# odstranění oanotovaných testovacích dat, která byla zaslána mnohem
# dříve než dávka párů).
anotated:
	python3 remove-anotated.py 'all-pairs.tsv' 'anotator-testing-data.tsv' > 'anotator-pairs-data.tsv'
