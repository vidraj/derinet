
# Soubory derivátů k ruční anotaci

## Data k anotaci
| Soubor | Obsah | K anotaci dodáno jako |
| --- | --- | --- |
| `all-more-minus-wikt.tsv` | sirotci s více rodiči (tzn. dávka 1) a s odebranými již oanotovanými daty z wiktionary dávky 1 | balíček 2 (_květen_) |
| `all-more-parent.tsv` | sirotci s více rodiči (dávka 1)| |
| `all-one-minus-wikt.tsv` | sirotci s jedním rodičem (tzn. dávka 0) a s odebranými již oanotovanými daty z wiktionary dávky 0 | balíček 1 (_květen_) |
| `all-one-parent.tsv` | sirotci s jedním rodičem (dávka 0)| |

## Základní informace
Vytvořeno pomocí `prepare/Makefile`. Stačí zadat: `make all`, popřípadě prostudovat jednotlivé targety.

*Důležitá poznámka:* Data SSJČ nejsou součástí kvůli jejich licenci, je nutné je rozbalené dodat do adresáře `prepare/`.

Skripty:
1. extrahují české morfologické derivační vztahy ze [SSJČ](http://ssjc.ujc.cas.cz/);
2. porovnají tato jednotlivá data s daty DeriNetu (soustředí se na potenciální rodiče pro derinetí sirotky), z čehož vytvoří seznamy sirotků a jejich potenciálních rodičů (rozdělené na kompozita a nekompozita);
3. vytvoří seznamy (z nekompozit) k ruční anotaci (viz tabulka výše).

Vedlejším produktem může být seznam lexémů, které v DeriNetu nejsou, ale v SSJČ ano, popřípadě seznam kompozit a jejich derivačních vztahů atd.
