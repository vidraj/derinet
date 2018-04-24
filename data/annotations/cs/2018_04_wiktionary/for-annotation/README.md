# Soubory derivátů k ruční anotaci

## Data k anotaci
| Soubor | Obsah | K anotaci dodáno jako |
| --- | --- | --- |
| `all-more-parent.tsv` | sirotci s více rodiči | balíček 2 (_květen_) |
| `all-one-minus-testing.tsv` | sirotci s jedním rodičem a s odebranými již oanotovanými testovacími daty dávky 0 | balíček 1 (_duben_) |
| `all-one-parent.tsv` | sirotci s jedním rodičem | |
| `anotator-testing.tsv` | sirotci s jedním rodičem - testovací data (dávka 0) | balíček 0 (_březen_) |

*Důležitá poznámka:* soubor `anotator-testing.tsv` byl vytvořen lehce upraveným skriptem `prepare/one-parent.py`, tyto úpravy ale již nejsou zachovány, a tak nedoporučuji tato testovací data mazat.

## Základní informace
Vytvořeno pomocí `prepare/Makefile`. Stačí zadat: `make all`, popřípadě prostudovat jednotlivé targety.

Skripty:
1.  stáhnou potřebná data z [WikiMedia dumps](https://dumps.wikimedia.org/backup-index.html) (release z 20. ledna 2018);
2. extrahují české morfologické derivační vztahy z české, anglické, francouzské, německé a polské mutace [Wiktionary](https://www.wiktionary.org/);
3. porovnají tato jednotlivá data s daty DeriNetu (soustředí se na potenciální rodiče pro derinetí sirotky), z čehož vytvoří pro každou jazykovou mutaci seznamy sirotků a jejich potenciálních rodičů (rozdělené na kompozita  a nekompozita);
4. sloučí tyto vytvořené seznamy v jeden;
5. vytvoří seznamy k ruční anotaci (viz tabulka výše).

Vedlejším produktem může být seznam sloučených lexémů, které v DeriNetu nejsou, ale v některé z mutací Wiktionary ano.

Skripty pro bod 1 a 2 pochází z repozitáře: [wiktionary-wf](https://github.com/lukyjanek/wiktionary-wf). Tam je aktualizován, zde je jeho statická varianta (ke 24.04.2018).
