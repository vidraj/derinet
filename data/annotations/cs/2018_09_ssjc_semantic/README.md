Stále probíhá příprava a zpracování.

# Extrakce sémantických labelů ze SSJČ
Anotační sada přidávající sémantické labely ze SSJČ. Hlavní anotace prováděna automaticky. Následně potenciálně manuální kontrola. Extrahována deminutiva, přechýlení, dokonavost, nedokonavost, násobení, substantivizace, zpodstatnění.

## Postup
1. extrakce potenciálních vztahů a jejich sémantických labelů
    - na základě vypozorovaných vzorů v semi-strukturovaných datech
    - **prepare/extract-ssjc.py** --> **for-annotation/potentials-ssjc.tsv**
    - **for-annotation/potentials-ssjc.tsv** sloupce: rodič - dítě - label
2. automatická anotace
    - automaticky přidány značky ke vztahům, které v DeriNetu existují
    - **prepare/annotate.py** --> **for-annotation/semantic-labels-ssjc.tsv**
    - **for-annotation/semantic-labels-ssjc.tsv** sloupce: značka - rodič - dítě - label
3. vícenásobné sémantické značení
    - kontrola vztahů s více sémantickými labely
    - **prepare/multiple-labels.py** --> **for-annotation/multiple-labeled-ssjc.tsv**
    - **for-annotation/multiple-labeled-ssjc.tsv** sloupce: rodič - dítě - label1 - label2 - ... - labelN
4. manuální opravy
    - manuální zásahy (opravy slovních druhů, vícenásobného labelování atd.)

# Extrakce sémanických labelů z MorfFlexCZ (z t-lemmatu DeriNetu)
Anotační sada přidávající sémantické značky z t-lemmatu Derinetu. Hlavní anotace prováděna automaticky. Následně potenciální manuální kontrola. Extrahována deminutiva, posesiva, přechálení.

## Postup
1. extrakce potenciálních vztahů a jejich sémantických labelů
    - na základě značek (^DI, ^FM) v t-lemmatu, zároveň rekonstruovány rodiče
    - **prepare/extract-morfflex.py** --> **for-annotation/potentials-morfflex.tsv**
    - **for-annotation/potentials-t-derinet.tsv** sloupce: rodič - dítě - label
2. automatická anotace
    - automaticky přidány značky ke vztahům, které v DeriNetu existují
    - **prepare/annotate.py** --> **for-annotation/semantic-morfflex.tsv**
    - **hand-annotated/semantic-labels-morfflex.tsv** sloupce: značka - rodič - dítě - label
3. vícenásobné sémantické značení
    - kontrola vztahů s více sémantickými labely
    - **prepare/multiple-labels.py** --> **for-annotation/multiple-labeled-morfflex.tsv**
    - **for-annotation/multiple-labeled-morfflex.tsv** sloupce: rodič - dítě - label1 - label2 - ... - labelN
4. manuální opravy
    - manuální zásahy (opravy slovních druhů, vícenásobného labelování atd.)

# Extrakce sémanických labelů z Příruční mluvnice češtiny (z t-lemmatu DeriNetu)
Anotační sada přidávající sémantické značky manuálně získané z Derinetu. Hlavní anotace prováděna manuálně. Extrahována deminutiva, posesiva.

## Postup
1. extrakce potenciálních vztahů a jejich sémantických labelů
    - na základě koncovek morfémů (koncovky z PMČ), rodiče přidány z DeriNetu
    - **prepare/extract-pmc.py** --> **hand-annotated/potentials-pmc.tsv**
    - **hand-annotated/semantic-labels-pmc.tsv** sloupce: značka - rodič - dítě - label
2. vícenásobné sémantické značení
    - kontrola vztahů s více sémantickými labely
    - **prepare/multiple-labels.py** --> **for-annotation/multiple-labeled-pmc.tsv**
    - **for-annotation/multiple-labeled-pmc.tsv** sloupce: rodič - dítě - label1 - label2 - ... - labelN
3. manuální anotace
    - manuálně oanotováno


# Anotační značky a sémantické labely
## Anotační značky
| značka | vysvětlivka |
| - | - |
| PRÁZDNO |  vztah v DeriNetu není, nebo nebyl manuálně anotován; nepřidávat sémantický label |
| % | vztah je v DeriNetu; přidat sémantické label |
| @ | label pro vztah byl manuální anotací označen za špatný; nepřidávat sémantické label |

## Sémantické labely
Platí pro vztah (sloupce: anot. značka - rodič - dítě - label), respektive pro dítě vdaném vztahu.
| značka | vysvětlivka |
| - | - |
| zdrob. | zdrobnělina |
| zpodst. | zpodstatnělé |
| podst. | substantivizace |
| nás. | násobení |
| dok. | dokonavost |
| ned. | nedokonavost |
| přech. | přechýlení |
| poses. | posesivum |


# Sloučení extrahovaných dat a přidání příznaků
Zpracování extrahovaných dat a předpříprava pro strojové učení.

## Sloučení
Sloučení všech extrahovaných a anotovaných dat tak, aby v datech nebyly duplicity vztahů. Výstupem data pozitivních (sémanticky labelovaných) příkladů bez duplicit. **hand-annotated/semantic-labels.tsv** sloupce: pozitivníznačka - rodič - dítě - label

## Příznaky
Přidání relevantních příznaků pro strojové učení.
Rodič z DeriNetu přidán při přípravě dat, stejně tak slovní druh (N=noun, A=adjective, V=verb, D=adverb) dítěte a rodiče.
Rod (M=masculine animate, I=masculine inanimate, F=feminine, N=neuter) přidán ze SYN2015, pouze k substantivům (v případě více možností vybrán nejfrekventovanější).
N-gramové rozložení konce slov zatím od 1-gram do 6-gram.




# Poznámky ke skriptům, návrhu anotační sady a postupu práce
- hvězdička * znamená "použít"

- statistiky
    - z release 1.6 bylo automaticky oanotováno 9,176 vztahů sémantickým labelem
        - z toho 9 vztahů se 2 sémantickými labely
    - z releasu 1.7 bylo automaticky oanotováno 9,903 vztahů sémantickým labelem
        - z toho 9 vztahů se 2 sémantickými labely
        - zdrob.   2,783    *
        - zpodst.  149
        - podst.   1,009
        - nás.     1,508    *
        - dok.     263
        - ned.     3,131
        - přech.   1,209    *

- v t-lemmatu DeriNetu
    - grep '\^DI\*\*'    adresáříček_,e_^(^DI*3k)           659     zdrob.  *
    - grep '\^FM\*\*'    agrobioložčin_^(^FM*3g)_(*3ka)_    589     fem.přivl. (+přech.)    *
    - grep '\^FC\*\*'    pštrosice_^(^FC*3)                 10      přech    *

- manuálně
    - přidat přivlasťovací jména 'ův', 'in' - přivl. adj.   *
    - nesubstantivní vnitřně-slovně-druhové sémanticé vztahy (u zdrob.) - přidat z Příruční mluvnice češtiny

- features (kart. souč.?)

- možnost přidat deminutiva na základě SFG Adély Kalužové (vyžadovalo by obsáhlejší manuální anotaci)



- afixy z PČM
PŘÍRUČNÍ MLUVNICE ČEŠTINY
deminutiva:
N: -ek, -ík, -ka, -ko, -átko, -eček, -íček, -ička, -ečka, -íčko, -ečko, -éčko, -ánek, -ínek, -áček, -enka, -inka, -oušek, -uška
A: -ičký, -oučký, -inký, -ounký, -ičičký, -ilinký, -oulinký, -ouninký, -inkatý
V: -kat, -itat, -etat, -inkat
přechýlení:
N: -ka, -ice, -nice, -yně, -kyně, -ovna, -na, -ová, -ice, -e, -ě
posesiva:
A: -ův, -ova, -ovo, -ic, -in, -ina, -ino, -í, -cí, -čí, -ský, -ový, -ký, -ovský

- afixy z CzechEncy.org
CZECHENCY
https://www.czechency.org/slovnik/DEMINUTIVUM
https://www.czechency.org/slovnik/POSESIVN%C3%8D%20-%C3%8D-ADJEKTIVUM
https://www.czechency.org/slovnik/POSESIVN%C3%8D%20-%C5%AEV-/-IN-ADJEKTIVUM
https://www.czechency.org/slovnik/P%C5%98ECH%C3%9DLEN%C3%89%20N%C3%81ZVY
deminutiva:
‑ek, ‑ík, ‑ka, ‑ko, ‑átko, ‑eček, ‑ečka, ‑ečko, ‑éčko, ‑íček, ‑ička, ‑íčko, ‑ičko, ‑áček, ‑ínek, ‑inka, ‑ínko, ‑inko, ‑enka, ‑ánek, ‑oušek, ‑uška
posesiva:
-ův, -in, -ov, -í
přechýlení:
‑ka, ‑ovka, ‑nice, ‑yně, ‑kyně, ‑ová, ‑ice
