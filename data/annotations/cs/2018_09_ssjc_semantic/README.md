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
    - **for-annotation/semantic-labels-morfflex.tsv** sloupce: značka - rodič - dítě - label
3. vícenásobné sémantické značení
    - kontrola vztahů s více sémantickými labely
    - **prepare/multiple-labels.py** --> **for-annotation/multiple-labeled-morfflex.tsv**
    - **for-annotation/multiple-labeled-morfflex.tsv** sloupce: rodič - dítě - label1 - label2 - ... - labelN
4. manuální opravy
    - manuální zásahy (opravy slovních druhů, vícenásobného labelování atd.)

- v t-lemmatu DeriNetu
    - grep '\^DI\*\*'    zdrob., např. adresáříček_,e_^(^DI*3k)
    - grep '\^FM\*\*'    fem. a přech, např. agrobioložčin_^(^FM*3g)_(*3ka)_
    - grep '\^FC\*\*'    přech., např. pštrosice_^(^FC*3)

# Extrakce sémanických labelů z Příruční mluvnice češtiny
Anotační sada přidávající sémantické značky manuálně získané z Derinetu na základě afixů z PMČ. Hlavní anotace prováděna manuálně. Extrahována deminutiva (adjektivní, slovesná a adverbiální) a posesiva.

## Postup
1. extrakce potenciálních vztahů a jejich sémantických labelů
    - na základě koncovek morfémů (koncovky z PMČ), rodiče přidány z DeriNetu
    - **prepare/extract-pmc.py** --> **for-annotation/potentials-pmc.tsv**
    - **for-annotation/semantic-labels-pmc.tsv** sloupce: značka - rodič - dítě - label
2. vícenásobné sémantické značení
    - kontrola vztahů s více sémantickými labely
    - **prepare/multiple-labels.py** --> **for-annotation/multiple-labeled-pmc.tsv**
    - **for-annotation/multiple-labeled-pmc.tsv** sloupce: rodič - dítě - label1 - label2 - ... - labelN
3. manuální anotace
    - manuálně oanotováno

- vztahy z derinetu (viz Poznámky)
    - potomci končící na -ův, -in
    - potomci končící na (adjektivní, slovesné a příslovečné) deminutivní affixy (z PMČ)

# Extrakce sémantických labelů z VALLEX3
Anotační sada přidávající sémantické labely z VALLEX3. Hlavní anotace prováděna automaticky. Následně manuální kontrola. Extrahována dokonavost, nedokonavost, násobení.

## Postup
1. extrakce potenciálních vztahů a jejich sémantických labelů
    - strukturovaná data (permutace všech dvojic v každém slovesném clusteru)
    - **prepare/extract-vallex.py** --> **for-annotation/potentials-vallex.tsv**
    - **for-annotation/potentials-vallex.tsv** sloupce: rodič - dítě - label
2. automatická anotace
    - automaticky přidány značky ke vztahům, které v DeriNetu existují
    - **prepare/annotate.py** --> **for-annotation/semantic-labels-vallex.tsv**
    - **for-annotation/semantic-labels-vallex.tsv** sloupce: značka - rodič - dítě - label
3. vícenásobné sémantické značení
    - kontrola vztahů s více sémantickými labely
    - **prepare/multiple-labels.py** --> **for-annotation/multiple-labeled-vallex.tsv**
    - **for-annotation/multiple-labeled-vallex.tsv** sloupce: rodič - dítě - label1 - label2 - ... - labelN
4. manuální opravy

# Anotační značky a sémantické labely
## Anotační značky
| značka | vysvětlivka |
| - | - |
| PRÁZDNO |  vztah v DeriNetu není, nebo nebyl manuálně anotován; nepřidávat sémantický label |
| % | vztah je v DeriNetu; přidat sémantické label |
| @ | label pro vztah byl manuální anotací označen za špatný; nepřidávat sémantické label |

## Sémantické labely
Platí pro vztah (sloupce: anot. značka - rodič - dítě - label), respektive pro dítě vdaném vztahu.

| značka | vysvětlivka | výstupní label |
| - | - | - |
| zdrob. | zdrobnělina | DIMINUTIVE |
| zpodst. | zpodstatnělé |  |
| podst. | substantivizace |  |
| nás. | násobení | ITERATIVE |
| dok. | dokonavost | ASPECT |
| ned. | nedokonavost | ASPECT |
| přech. | přechýlení | FEMALE |
| poses. | posesivum | POSSESSIVE |


# Sloučení extrahovaných dat, přidání příznaků, závěrečná manuální anotace
Zpracování extrahovaných dat a předpříprava pro strojové učení.

## Sloučení
Sloučení všech extrahovaných a anotovaných dat tak, aby v datech nebyly duplicity vztahů. Výstupem data pozitivních (sémanticky labelovaných) příkladů bez duplicit. **for-annotation/semantic-labels.tsv** sloupce: pozitivníznačka - rodič - dítě - label - opravený label (je-li potřeba)

## Příznaky
Přidání relevantních příznaků pro strojové učení.
Rodič z DeriNetu (dáno automatickou anotací, u PMC dáno počáteční extrakcí) přidán při přípravě dat, stejně tak slovní druh (N=noun, A=adjective, V=verb, D=adverb) rodiče a dítěte. Ze slovního druhu byl odebrán příznak C (kompozitnosti).
Rod (M=masculine animate, I=masculine inanimate, F=feminine, N=neuter) přidán na základě analýzy MorphoDiTa (vyskytuje se u substantiv a neposesivních adjektiv).
Vid (P=perfective, I=imperfective, B=both) přidán na zákládě analýzy SYN2015 pouze ke slovesům (v případě více možností vybrán nejfrekventovanější pro dané lemma).
N-gramové rozložení začátků a konců slov (zatím) od 1-gram do 6-gram.
Začátek velkým písmenem (1=proprium, 0=non-proprium).
Totožný začátek (1-gram) dítěte a rodiče (1=same_begin, 0=different_begin).

Značka "-" znamená nespecifikovaný příznak.
Slovní druhy, rody a vidy jsou ve tvaru kartézského součinu (RodičxDítě). Například: pokud je rodič adjektivum a dítě substantivum, výsledný příznak je AN.

## Manuální anotace
Pomocí doplněných příznaků byla data ještě jednou zkontrolována (např. zda odpovídá vid u vztahů dok. a ned., zda odpovídá rod u přech. atp.) a na základě toho byla provedena poslední oprava/úprava, respektive anotace dat.
V případě nesprávného labelu byl v souboru **for-annotation/semantic-labels.tsv** přidán do posledního (pátého) sloupce opravený label a data přegenerována, aby obsahovala opravené labely.
Oprava chybně doplněných feature byla provedena do souboru **for-annotation/feature-corrections.tsv**, odkud byla pomocí skriptu **prepare/correct-features.py** aplikována na data **for-annotation/MLdata-semantic-labels.tsv**, čímž vznikla jejich opravená verze pro strojové učení: **hand-annotated/MLSemLab.tsv**.

# Strojové učení


# Poznámky
- možnost přidat deminutiva na základě SFG Adély Kalužové (vyžadovalo by obsáhlejší manuální anotaci)
- možnost přidat iterativa a (im)perfektiva z VALLEX 3.0

- poznámky k sémantickým labelům ([PMČ] & [B]AGASHEVA & Czech[E]ncy)
    - deminutiva {B: DIMINUTIVE}
        - PMČ S: [kopeč-ek, meč-ík, včel-ka, prádél-ko, kopýt-ko, hříb-átko, háječ-ek, bratř-íček, věc-ička, šňůr-ečka, aut-íčko, oč-ičko, jabl-éčko, nos-ánek, tat-ínek, syn-áček, šavl-enka, tet-inka, děd-oušek, dcer-uška]
        - PMČ Sp: [Jarosláv-ek, Jiř-ík, Han-ka, Pep-íček, Ev-ička, Pep-ánek, Joží-nek, Ferd-áček, Mař-enka, Jar-oušek]
        - PMČ A: [mlad-ičký, mlaď-oučký, mlad-inký, mlaď-ounký, mal-ičičký, mal-ilinký, slab-oulinký, slab-ouninký, mal-inkatý]
        - PMČ A: [šed-avý, na-červena-lý, při-hloup-lý, za-špičatě-lý, polo-suchý, kvazi-revoluční]
        - PMČ V: [cap-k-at, tlap-k-at, ťap-k-at, šp-it-at, štěb-et-at, haj-ink-at, ]
        - E pro D [mal-ičko]
        - E: primární [keř-ík] a sekundární [keř-íč-ek] deminutiva
        - zatím nezahrnout:
            - PMČ A: [prach-bídný, pra-hloupý, hlubok-ánský, pře-vysoký, sebe-dokonal-ejší, ultra-radikální, super-malý, supra-vodivý, hyper-korektní] {AUGMENTATIVE}
            - PMČ V: [šveh-olit, mrh-olit, bat-olit, drm-olit] {DIMINUTIVE} - nemají slovesného rodiče
            - PMČ V nespecifikovaná míra [po-cvičit, po-pudit, po-soudit] {DIMINUTIVE}
            - PMČ V malá míra (k již prefigovanému V) [po-odejít, po-vyrůst] a [po-hubnout, po-bolívat, po-tloukat] a [na-říznout, na-trhnout] a [na-bourat, na-hlodat, na-hnout] {DIMINUTIVE}
            - PMČ V neúplná míra [při-brzdit, při-hladit, při-pálit] {DIMINUTIVE}
            - PMČ V substandardní míra [pod-dimenzovat, pod-hustit] {DIMINUTIVE}
            - PMČ V nedostatečná míra [nedo-myslet, nedo-slýchat] {DIMINUTIVE}
            - PMČ V velká míra [na-dělat, na-běhat, na-dělat] {AUGMENTATIVE}
            - PMČ V nadstandardní míra [pře-chladit, pře-sytit, nad-cenit, vyna-koukat] {AUGMENTATIVE}
            - u prefixů V není stále zřejmý význam
            - u prefixů A není vyjasněna míra (význam prefixu významem kořene; DIMINUTIVE vs. AUGMENTATIVE)
            - ? B AUGMENTATIVE mj. [bg. mažiše = en. huge man = cs. mužnější] -> flexe (ale nikde není nej-x-ší)
        - E: "Deminutivní (n. deminutivně-iterativní) skupina obsahuje deminutiva, která spojují opakovanost děje s oslabovací významovou složkou: poblýskávat, pozpěvovat, pospávat aj."

    - iterativa {B: ITERATIVE}
        - PMČ: tvoří se k imperfektivům [vídá-va-t, slýchá-va-t, hubová-va-t, tvrdí-va-t, sní-va-t, vrací-va-t, hřá-va-t, pásá-va-t]
        - E [jíd-a-t, čít-a-t, víd-a-t]
        - ošetřit prefixy sloves (pokud se liší prefixem, nejde o iterativa),
        - E: "sémantickou kategorii slovesa, jejíž status není dosud zcela jasný" (způsob děje vs. kategorie vidu)
        - E: stylistické/reduplikativní [dělá-vá-vá-vá-vá-va-t]
        - E: iterativa nemění vid svého rodiče a nelze jimi vyjádřit přítomnost; -va- slouží také ke změně vidu (tzv. sekundární imperfektiva) [zkrac-ova-t, dá-va-t] a lze jimi vyjádřit přítomnost, což iterativy nelze

    - (im)perfektivizace {B: ???} {ASPECT}
        - přidat ze SSJČ
        - zkontrolovat opačnost hran v SSJČ
        - E: "Vedle vidových párů se v č. vyskytují také vidové trojice typu hradit (nedok.) × nahradit (dok.) × nahrazovat (nedok.); blížit se (nedok.) × přiblížit se (dok.) × přibližovat se (nedok.). U těchto trojic existují tedy dublety v nedok. v., které jsou víceméně synonymní: hradit a nahrazovat, blížit se a přibližovat se. Patrně tady jde o rezultát koexistence a konkurence dvou různých prostředků pro tvoření vidových dvojic"

    - přechýlení {B: FEMALE}
        - PMČ ženské protějšky [soud-kyně, logist-ička, uprchl-ice, boh-yně, král-ovna, kvěž-na, hospodsk-á, doktor-ová]
        - PMČ ženská příjmení [Vybíral-ová, Kočí, Gorvačov-ová, Tolst-á, Kowalsk-á]
        - PMČ jména zvířat [holub-ice, sam-ice, orl-ice] a [čert-ice, ďábl-ice]

    - posesiva {B: POSSESSIVE}
        - PMČ individuálně posesivní [pán-ův, Karl-ův, matč-in, Věř-in]
        - zatím nezahrnout:
            - PMČ druhově posesivní [rač-í, ovč-í, tele-cí, jehně-čí, krav-ský, vepř-ový, chlape-cký, snob-ský, slouh-ovský, otc-ovský] -> muselo by jít o ty -í, které nemají sourozence -in/-ův (viz struktralismus forma-funkce)
            - E: u druhově posesivních -í pro zvířata, -ský pro lidi

    - nezahrnout: jiný label
        - {MALE} PMČ mužské protějšky [vdova -> vdov-ec, husa -> hous-er, koza -> koz-el]; E [myš -> myš-ák]
        - {YOUNG} PMČ přechylováním neuter [ptáč-e, vlč-e, cikán-ě, kachn-ě, hříb-ě]; E [pod-svin-če]
        - {SIMILATIVE} PMČ individuálně posesivní, ale význam podobnosti [kafk-ovský]; E [otc-ovský]

    - nazahrnout: vztahová adj. {B: RELATIONAL}
        - PMČ vztah k místu [podzem-ní, moř-ský, ameri-cký, niger-ijský]
        - PMČ nespecifikovaný vztah [prosinc-ový, dopis-ní, loupež-ný]
        - PMČ vztah k látce [slam-ěný, kož-ený, želez-ný, ricin-ový]
