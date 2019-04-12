# First experiment with Machine Learning for semantic labelling word-formation relations in DeriNet
This folder contains codes of a supervised machine-learning approach to semantic labelling of word-formation relations in DeriNet.
The work consists of:
1. data preprocessing (data extraction from linguistically representative resources, annotation of extracted data, adding relevant features to the data, dividing data to train/development/test sets),
2. machine-learning experimenting with various methods for classification,
3. labelling word-formation relations in DeriNet, and
4. evaluation.

Each step is well-documented and commented bellow and in **Makefile**.

*Supported by Student's Faculty Grant (SFG) at [Faculty of Mathematics and Physics, Charles University](https://www.mff.cuni.cz/), in the academic year 2018/2019.*

## Data preprocessing
### Data extraction
#### From *Slovník spisovného jazyka českého*
Adds semantically labelled relations from SSJČ. The annotation has been done automatically (see bellow).
Extracted: diminutive, female names, possessive, imperfectivization, perfectivization, iterativity, substantivization.

1. collecting candidates and their semantic labels
    - from semi-sructured data of an electronic version of SSJČ
    - **prepare/extract-ssjc.py** --> **for-annotation/potentials-ssjc.tsv**
    - **for-annotation/potentials-ssjc.tsv** columns: parent - child - label
2. automatic annotation
    - **prepare/annotate.py** --> **for-annotation/semantic-labels-ssjc.tsv**
    - **for-annotation/semantic-labels-ssjc.tsv** columns: annotation-mark - parent - child - label
3. check (and manually fix) relations with more semnatic labels
    - **prepare/multiple-labels.py** --> **for-annotation/multiple-labeled-ssjc.tsv**
    - **for-annotation/multiple-labeled-ssjc.tsv** columns: parent - child - label1 - label2 - ... - labelN

#### From *MorfFlex CZ*
Adds semantically labelled relations from morphological dictionary MorfFlex CZ. The annotation has been done automatically (see bellow).
Extracted: diminutive, female names, possessive.

1. collecting candidates and their semantic labels
    - from sructured data; parents reconstructed from morphological lemmas
    - labels base on marks: ^DI = diminutives, ^FM = female names and possessive, ^FC = female names
    - **prepare/extract-morfflex.py** --> **for-annotation/potentials-morfflex.tsv**
    - **for-annotation/potentials-t-derinet.tsv** columns: parent - child - label
2. automatic annotation
    - **prepare/annotate.py** --> **for-annotation/semantic-morfflex.tsv**
    - **for-annotation/semantic-labels-morfflex.tsv** columns: annotation-mark - parent - child - label
3. check (and manually fix) relations with more semnatic labels
    - **prepare/multiple-labels.py** --> **for-annotation/multiple-labeled-morfflex.tsv**
    - **for-annotation/multiple-labeled-morfflex.tsv** columns: parent - child - label1 - label2 - ... - labelN

#### From *VALLEX*
Adds semantically labelled relations from VALLEX3. The annotation has been done automatically (see bellow).
Extracted: perfectivization, imperfectivization, iterativity.

1. collecting candidates and their semantic labels
    - from sructured data
    - labels base on marks: ^DI = diminutives, ^FM = female names and possessive, ^FC = female names
    - **prepare/extract-vallex.py** --> **for-annotation/potentials-vallex.tsv**
    - **for-annotation/potentials-vallex.tsv** columns: parent - child - label
2. automatic annotation
    - **prepare/annotate.py** --> **for-annotation/semantic-labels-vallex.tsv**
    - **for-annotation/semantic-labels-vallex.tsv** columns: annotation-mark - parent - child - label
3. check (and manually fix) relations with more semnatic labels
    - **prepare/multiple-labels.py** --> **for-annotation/multiple-labeled-vallex.tsv**
    - **for-annotation/multiple-labeled-vallex.tsv** columns: parent - child - label1 - label2 - ... - labelN

#### From *Příruční mluvnice češtiny*, *Slovník afixů užívaných v češtině*, *Nový encyklopedický slovník češtiny*
Adds semantically labelled relations from paper publication: *Příruční mluvnice češtiny*, *Slovník afixů užívaných v češtině*, *Nový encyklopedický slovník češtiny*. The annotation has been done manually (see bellow).
Extracted: diminutive (of adjectives, verbs, adverbs), possessive.

1. manual extraction of formal patterns from mentioned paper publications
    - see bellow to the Section **Czech notes about extracted patterns from paper publications** (written in Czech)
2. collecting candidates and their semantic labels
    - from from sructured data of DeriNet
    - labels base on extracted patterns
    - **prepare/extract-pmc.py** --> **for-annotation/potentials-pmc.tsv**
    - **for-annotation/semantic-labels-pmc.tsv** columns: parent - child - label
3. manual annotation
    - **for-annotation/semantic-labels-pmc.tsv** columns: annotation-mark - parent - child - label
4. check (and manually fix) relations with more semnatic labels
    - **prepare/multiple-labels.py** --> **for-annotation/multiple-labeled-pmc.tsv**
    - **for-annotation/multiple-labeled-pmc.tsv** columns: parent - child - label1 - label2 - ... - labelN

#### From *DeriNet*
Adds semantically labelled relations (negative exmaples) from DeriNet. The annotation has been done manually (see bellow).
Extracted: relations which are not diminutive, female names, possessive, imperfectivization, perfectivization, iterative.
These candidates serves as negative examples for machine-learning approach.

1. collecting candidates and their semantic labels
    - from sructured data
    - **prepare/add-negatives.py** --> **for-annotation/negatives-derinet.tsv**
    - **for-annotation/negatives-derinet.tsv** columns: parent - child - label
2. manual annotation
    - **for-annotation/negatives-derinet.tsv** columns: annotation-mark - parent - child - label


### Annotation of candidates
#### Automatic annotation
The automatic annotation means, that each candidate relation was automaticaly checked whether it is in DeriNet. If yes, than candidate is accepted, otherwise unaccepted. It was used for large data extracted from SSJČ, MorfFlex CZ and VALLEX.

#### Manual annotation
The manual annotaion means, that each candidate relation was manually checked and annotated. It was used for data extracted from DeriNet based on above-mentioned paper publications.

#### Annotation marks (independent on type of annotation)
| annotation mark | meaning |
| - | - |
| EMPTY |  unaccept candidate (the candidate relation is not in DeriNet) |
| % | accept candidate (the candidate is in DeriNetu or it was manually accepted) |
| @ | unaccept candidate (the candidate was manually unaccepted) |

### Selecting of relevant semantic labels
Inspired by Bagasheva (2017), 5 semantic labels were selected based on extracted and annotated data.
Semantic label ASPECT was used as a compromise (Bagasheva uses more semantic labels for these relations) for further work.

| semantic label (detailed, Czech) | semantic label (universal, cross-lingual) | meaning | example |
| - | - | - | - |
| zdrob. | DIMINUTIVE | diminutive (zdrobnělina) | auto(Noun) > autíčko(Noun) |
| zpodst. | (not processed) | sustantivization (zpodstatnělé) | jehněčí(Adjective) > jehněčí(Noun) |
| podst. | (not processed) | substantivization (podstatné) | proměnný(Adjective) > proměnnost(Noun) |
| nás. | ITERATIVE | iterative of verbs (násobení/iterativnost) | zbývat(Verb) > zvývávat(Verb) |
| dok. | ASPECT | perfectivization (zdokonavění) | čichat(Verb) > čichnout(Verb) |
| ned. | ASPECT | imperfectivization (znedokonavění) | oddat(Verb) > oddávat(Verb) |
| přech. | FEMALE | female names (přechýlení) | manžel(Noun) > manželka(Noun) |
| poses. | POSSESSIVE | possessive (přivlastnění) | otec(Noun) > otcův(Adjective) |
| non-lab. | none | technical label for ML-approach; relations which are not DIMINUTIVE, ITERATIVE, ASPECT, FEMALE, POSSESSIVE | |

### Preprocessing of the data
Data was merged and checked whether it contains multiple-labelled relations. Potential multiple-labeled relation were fixex.
File **for-annotation/semantic-labels.tsv** (columns: accepted-annotation-mark - parent - child - label - fixed-label (if necessary)) contains all merged positive examples for machine-learning approach.

Then, each relation in the data was enlarged with relevant features.

| feature | values | comment |
| - | - | - |
| part-of-speech of child | N (noun), A (adjective), V (verb), D (adverb) | source: DeriNet |
| part-of-speech of parent | N (noun), A (adjective), V (verb), D (adverb) | source: DeriNet |
| gender of child | M (masc. animate), I (masc. inanim.), F (feminine), N (neuter) | source: MorfFlex CZ using MorphoDiTa; only for nouns |
| gender of parent | M (masc. animate), I (masc. inanim.), F (feminine), N (neuter) | source: MorfFlex CZ using MorphoDiTa; only for nouns |
| aspect of child | P (perfective), I (imperfective), B (biaspectual) | source: MorfFlex CZ using MorhoDiTa, SYN2015, VALLEX; only for verbs |
| aspect of parent | P (perfective), I (imperfective), B (biaspectual) | source: MorfFlex CZ using MorhoDiTa, SYN2015, VALLEX; only for verbs |
| possessivy tag of child | 1 (possesive), 0 (not possessive) | source: MorfFlex CZ using MorhoDiTa |
| possessivity tags of parent | 1 (possesive), 0 (not possessive) | source: MorfFlex CZ using MorhoDiTa |
| same start | 1 (same 2 letters on starts), 0 (otherwise) | |
| same end | 1 (same 2 letters on ends), 0 (otherwise) | |
| n-grams of child from its start | uni-, bi-, tri-, tetra-, penta-, hexa-grams | |
| n-grams of child from its end | uni-, bi-, tri-, tetra-, penta-, hexa-grams | |
| n-grams of parent from its start | uni-, bi-, tri-, tetra-, penta-, hexa-grams | |
| n-grams of parent from its end | uni-, bi-, tri-, tetra-, penta-, hexa-grams | |
| semantic label | DIMINUTIVE, FEMALE, POSSESSIVE, ASPECT, ITERATIVE, none | |

If any of values was not present, then NA value was assign.
Some of added features (in semantically labeled data) were semi-automatically checked and manually corrected (see **for-annotation/feature-corrections.tsv**) Final semantically labeled data occurs in **hand-annotated/MLSemLab.tsv**.

### Dividing data
Data was (during the machine-learning experiments) divided on three data sets (with no overlaps):
- 80% training data
- 10% development data
- 10% test data


## Machine learning model
The decision to focus only on suffixation was made because of a huge dimensionality in case of prefixation or circumfixation (and because of extracted data).

After various experiments:
- these features were selected for the final model: part-of-speech of child, part-of-speech of parent, gender of child, gender of parent, aspect of child, aspect of parent, possessivity tags of parent, n-grams of child from its end (only: bi-, tri-, tetra-, penta-, hexa-grams), n-grams of parent from its end (only: bi-, tri-, tetra-, penta-grams), semantic label;
- as method, Multinomial logistic regression was chosen;
- these probability treshold for individual semantic label were selected based on development data: 0.75 for DIMINUTIVE, 0.4 for FEMALE, 0.4 for POSSESSIVE, 0.4 for ASPECT, and 0.5 for ITERATIVE.

Multinomial logistic regression reached following results on trainign and testing data:

| data set | accuracy | precision | recall | f1-score |
| - | - | - | - | - |
| training data set | 0.992 | 0.991 | 0.992 | 0.991 |
| evaluation test data | 0.986 | 0.984 | 0.984 | 0.984 |


## Labeling word-formation relations in DeriNet
Using **prepare/ml-for-prediction.py** all potential candidates for selected semantic labels were extracted and enlarged with relevant features. Then, trained model predict their semantic labels. The model assigned one of the five semantic labels to 150,521 derivational relations in total. The POSSESSIVE label was the most frequent one (predicted with 88,620 derivational relations), followed by the FEMALE label (28,510 rel.), ASPECT (15,459 rel.), ITERATIVE (11,890 rel.), and DIMINUTIVE (6,042 rel.)

## Evaluation
The precision and recall of the labelling procedure were evaluated on a randomly selected sample of 2,000 relations assigned either one of the five semantic categories or the none label. The accuracy was 0.971, the precision was 0.962, the recall was 0.963 and the f1-score was 0.962. Table bellow shows precision and recall for each semantic label.

| label | DIMINUTIVE | FEMALE | POSSESSIVE | ASPECT | ITERATIVE | none |
| - | - | - | - | - | - | - |
| precision | 0.969 | 0.982 | 0.999 | 0.987 | 0.985 | 0.948 |
| recall | 0.983 | 0.941 | 0.999 | 0.987 | 0.988 | 0.976 |

## Final semanticaly labeled data
List of prepared semantically labelled relations from DeriNet is listed in **hand-annotated/final-semantic-labels.tsv**.
The list is a result of initial experiments in field of semantic labelling using machine learning methods.
In this initial experiment, five semantic labels were predicted (DIMINUTIVE, FEMALE, POSSESSIVE, ASPECT, ITERATIVE).

### File format
The list of semantically labeled relations is saved to file `final-semantic-labels.tsv` in simple tab separated **.tsv** format.

The order of columns is as follow:
1. derivational parent (base word) with its part-of-speech tag separated by a dash,
2. derivationa child (derivative) with its part-of-speech tag separated by a dash,
3. predicted semantic label of the relation,
4. probability of predicted semantic label.

### Numbers of labelled relations for each semantic label
| Semantic label  | Count |
| ------------- | ------------- |
| DIMINUTIVE  | 6,042 |
| FEMALE  | 28,510 |
| POSSESSIVE | 88,620 |
| ASPECT | 15,459 |
| ITERATIVE | 11,890 |
| **total:** | **150,521** |


# Czech notes about some extracted patterns from paper publications
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
