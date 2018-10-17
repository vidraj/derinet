# Extrakce sémantických labelů ze SSJČ
Anotační sada přidávající sémantické labely ze SSJČ. Hlavní anotace prováděná automaticky. Následně manuální kontrola.

## Postup
1. extrakce potenciálních vztahů a jejich sémantických labelů
    - **prepare/extract-semantic.py** --> **for-annotation/potentials.tsv**
    - **for-annotation/potentials.tsv** sloupce: rodič - dítě - label
2. automatická anotace
    - automaticky přidány značky ke vztahům, které v DeriNetu existují
    - **prepare/annotate-semantic.py** --> **hand-annotated/semantic-labels.tsv**
    - **hand-annotated/semantic-labels.tsv** sloupce: značka - rodič - dítě - label

## Anotační značky a sémantické labely

### Anotační značky
| značka | vysvětlivka |
| - | - |
| PRÁZDNO |  vztah v DeriNetu není, nebo nebyl manuálně anotován; nepřidávat sémantický label |
| % | vztah je v DeriNetu; přidat sémantické label |
| @ | label pro vztah byl manuální anotací označen za špatný; nepřidávat sémantické label |

### Sémantické labely
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

## Poznámky ke skriptům, návrhu anotační sady a postupu práce
- postup
    - Potenciální vztahy a jejich labely lze extrahovat kdykoli, ale spuštění automatické anotace dává smysl až po tom, co budou do DeriNetu zahrnuta ručně anotovaná SSJČ data (2018_06_ssjc); při automatické anotaci nad releasem 1.6 je anotováno 9,6k vztahů. Vzhledem k postupnosti releasů, bude nutné vytvořit si interní mezi-verzi DeriNetu (obohacený release 1.6 o anotaci 2018_06_ssjc, interní chvilkový release 1.7), na níž bude provedena automatická anotace pro 2018_09_ssjc_semantic, a ta následně zahrnuta do publikovaného releasu 2.0.
- myšlenky schůzky 17.10.2018
    - Bezepčná cesta se sémantickými labely je zahrnout zatím pouze přech., zdrob. a nás. Ostatní labely nejsou špatně, ale...
    - Otazník visí nad přidáním ostatních vztahů daných labelů: pravidelnostně / strojové učení ?
    - Tato anotační sady si samozřejmě vyžádá změny v DeriNetím API i formátu (obojí verze 2.0) => olabelování ostatních vztahů daných labelů si nejspíš vyžádá přidat sloupec do formátu ver 1.7
