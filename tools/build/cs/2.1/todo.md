Anotace do DeriNetu před verzí 2.1
=============================

Release 2.0.5
-----------------

[LK, hotovo]
(Ne)motivovanost nejfrekventovanějích stromových kořenů (je z adresáře
2019_01_freq_roots/ přesunut do 2020_01_motivation_of_tree_root_nodes/).
Anotace má Lukáš (ze srpna 2019 a ledna 2020). Skript napíše Lukáš, Zdeněk
zkontroluje data, chce dalších 20000 řádků (od Šárky je anotovaných 6000).
Anotaci dalších 20k řádků provádí ZZ.
Přidat bit stromovým kořenům, které jsou skutečně potvrzeně nemotivované
(10. sloupec, položka 'Unmotivated=True'), přidat rodiče stromovým kořenům,
které jsou motivované (nové derivační vztahy), přidat bit stromovým kořenům,
které jsou kompozitem (10. sloupec, položka 'IsCompound=True', plus změnit
současnou variantu 'is_compound' na 'IsCompound'). Extrahovat varianty
a zažadit je do patřičné anotace (viz níže). Vytvořeny moduly:
*addcompoundmarks.py*, *addderivations.py*, *addunmotivatedmarks.py*,
*addcompounds2.py*.

[JV, hotovo]
Frekvence z korpusu. Máme absolutní frekvence, ale je potřeba dodělat další
skóre na jejich základě, viz e-mail od Zdeňka z března 2020.
Jmenovatel relativní frekvence by měla být velikost korpusu včetně čárek,
zájmen etc. Ale u kumulativní četnosti je jmenovatelem jenom počet slov
v DeriNetu. Zpracuje Jonáš; TODO tohle ještě probrat se Zdeňkem.
Problémy:
- pod jakým klíčem je chceme mít? Bylo to `CorpusCounts`, ale možná chceme
  kapitalizaci připodobnit JSONu víc než UD? Zavedl jsem hierarchii
  corpus_stats.absolute_count, corpus_stats.relative_frequency etc.
  (Možná by bylo lepší mít freq_count, freq_perc atd.)
- sparsity má v definici logaritmus, který je pro nulový abosolute_count
  nedefinovaný. Nekonečno nejde použít, protože se nedá uložit do JSONu.
  Jak to dodefinujeme? DBL_MAX? log(1/velikost korpusu)?

[LK, hotovo]
Slovesné třídy (2020_07_conjugation_class). Vezmou se z Lukášova
nástroje. Skript napíše Lukáš. Nechají se i přechody mezi třídami. Pro slovesa,
u kterých nástroj nedokáže určit třídu, nebude třída vyplněna.
Značka se vloží do sloupce morfologických kategorií jako "ConjugClass".
Vytvořen modul: *addconjugationclasses.py*.
- co použít za značku, pokud patří sloveso do více tříd zároveň?

[JV, hotovo]
Přechod na nový MorfFlex. Vezmeme aktuální verzi z Gitu a uvidíme, jestli to
bude průchozí. Zpracuje Jonáš.
Došlo k ~414426 změnám (podle V1 diff toolu, takže ve skutečnosti jich bude víc):
- odstraněno 8246 lexémů
- přibylo 16141 úplně nových lexémů a 2109 nových homonym k existujícím lexémům
- 465 slovům se změnilo techlemma a POS zároveň
  380268 se změnilo jenom techlemma,
  33 se změnil jenom POS.
- 7164 změn v derivacích:
    - 2103 odpojení (z toho 239 kvůli tomu, že základové slovo zmizelo; tedy
      1864 bylo prostě odpojeno)
    - 447 nově připojených
    - 4614 přepojení
Hodnocení správnosti změn:
- pro odstraňování lexémů většinou nevidím důvod
- nové lexémy jsou vlastní jména, hláskové varianty, nějaké drobnosti mimo
- nová homonyma jsou z velké části vlastní jména. Téměř nikde není uvedený důvod
  vyčlenění homonyma
- změny v POS a techlemma+POS vypadají dost arbitrárně, změny v techlemma jsem
  neprohlížel (je jich moc a není v tom na první pohled vidět systém)
- odpojení jsou většinou blbě
- nová připojení jsou vesměs správně
- přepojení jsou vesměs mezi homonymy

[JV, hotovo]
Vyjmenovaná slova (2019_12_06_enumerated_words). Smazat z výstupu počáteční
vy- a vý-, udělat z toho XLS soubor, kde se zaznačí předek, kompozitnost nebo
značka, že je to správně. Poslat rovnou Šárce (posláno 2020-07-10). Zpracovává
Jonáš.

[LK, hotovo]
Značka cizosti (2020_03_loanwords). Pomocí Lukášova pravidlového
nástroje se cizím lemmatům dá do sloupce morfologických kategorií značka
"Loanword=True". Vytvořen modul: *addloanwordmarks.py*.
- měla by se značka dědit? přidat Honzovy anotace z cognetu?

[JB, hotovo]
Segmentace. Vezmeme od pana Bodnára, až v půlce července odevzdá diplomku.
Jinak se různé manuální segmentace (kořenů) vyskytují v adresáři
2020_01_root_allomorphs_cleanup (hotovo v DeriNetu 2.0). Lukáš a Magda má také
poloautomaticky odsegmentované a ručně zkontrolované předpony u sloves.

[LK, hotovo]
Vymazání slov s překlepy: 2020_12_incorrect_lexemes. Další budou z anotací
variant. Modul: *delincorrectlexemes.py*

[LK, hotovo]
Přidání značky pro konverze (Type=Conversion) místo Type=Derivation.
Značka přidána jen u totožných stringů zavěšených na sobě.
Modul: *findconversion.py*

[LK, hotovo]
Změna tagsetu slovních druhů na Universal tagset. Modul: *changepostags.py*

[LK, hotovo]
Prefixace kořenů. Při manuálních anotacích cizích slov jsem si všiml spousty
prefigovaných kořenů bez rodičů; viz anotační dávka 2020_12_prefixed_words.
Nalezeny rodiče, zanotováno. Modul: *addderivations.py*




Release 2.0.6 (slouží jako 'interní' verze, hlavně pro analýzu variant)
-----------------

[LK, hotovo]
Varianty. 2021_01_spelling_variants. Pro každé hnízdo variant (např. extremismus,
extrémismus, extremizmus, extrémizmus) zvolit jedno základní a ostatní pověsit
přímo na něj. Takže citronový by viselo na citrónový, ne na citron, a mělo by
značku pro variantu.
- cs.AddVariants ../../../../data/annotations/cs/2021_01_spelling_variants/nsets-spelling-variants.tsv

[LK, hotovo]
Konverze. 2021_01_conversion. Nalezeny vztahy konverze a převěšeny správně.
Při té příležitosti odstraněna nesmyslná lemmata.
- cs.DelIncorrectLexemes ../../../../data/annotations/cs/2021_01_conversion/into-derinet/lexemes-to-delete.tsv
- cs.AddConversions ../../../../data/annotations/cs/2021_01_conversion/into-derinet/relations-of-conversion.tsv

[LK, hotovo]
Cizí slova. 2021_02_cognet_cognates + 2021_02_foreign_mark_to_loanword.
Sloučeny Loanwords a anotace kognátů od JB. Sloučena značka Foreign z
releasu 2.0 s Loanwords. Značka Foreign z dat odebrána. Značka Loanwords má
hodnoty True (je cizí slovo), False (není cizí slovo); pokud lemma nemá značku
Loanwords, znamená to, že neprošlo anotací. Bez značky Loanwords jsou také
všechna propria a celé jejich podstromy.
- cs.AddLoanwordMarks ../../../../data/annotations/cs/2021_02_cognet_cognates/hand-annotated/loanwords-trees-annotated.tsv
- cs.AddLoanwordMarks ../../../../data/annotations/cs/2021_02_foreign_mark_to_loanword/hand-annotated/loanwords-trees-annotated.tsv
- cs.CheckLoanwordPropriums
- cs.RemoveForeignMark

[LK, hotovo]
Oprava variant. 2021_01_spelling_variants. Analýza skriptem i vizualizací.
Ruční opravy v 2021_01_spelling_variants.



Release 2.0.7, příp. 2.1
-----------------

[LK, data předpřipravená, prodiskutovat, chybí moduly]
(Ne)motivovanost. 2020_01_motivation_of_tree_root_nodes. Fantomové lexémy a
vztahy s nimi spojené.
- jak založit fantomový lexém a nahrát vztahy s phantomovými rodiči?
- prodiskutovat phantomové rodiče z této anotace

[LK, nutné zkontrolovat a dokončit před vydáním]
Cizí slova. Některé lexémy, vlivem rozšiřování lemmasetu při přechodu na nový
MorfFlexCZ nemají značku Loanwords (byť by ji mít měly, protože jsou
malopísmenné). Je potřeba takové rodiny analyzovat a ručně doprojít podobně
jako předchozí dávky cizích slov.

[JV, předdomluvené]
Přechod na nový OFICIÁLNÍ MorfFlex. (viz LINDAT/CLARIAH)

[JV+LK, prodiskutovat]
Klíče a hodnoty. Prodiskutovat finální podobu klíčů a hodnot tak, aby je šlo
unifikovat napříč zdroji i v UDer. Ujasnit si význam sloupce pro OthRel. Dle
výsledků diskuze následně změnit schéma.




Nejsou, ale chtěli bychom (?)
-------------------------

K četnostem: Podívat se, kolik stromů se rozpadne, protože mají uprostřed slovo
bez korpusových výskytů.
Zkontrolovat stromy, jestli sedí sestupnost frekvencí. Někde to určitě nebude
sedět z dobrých lingvistických důvodů, ale jinde z toho můžeme dostat podezřelé
kandidáty.
Výsledky:
- celkem 26675 invertovaných párů lexémů
- z toho 3975 korpusově doložených uzlů visí na něčem nedoloženém
    - typicky jsou oba lexémy s podobnými počty, takže je to soft-fail
    - nebo jsou to vlastní jména, kde se to dá čekat:
      ```
      Havlíček_;Y#N   46316   Havlíčkův_;Y_^(*3ek)#A  201658
      Hyšpler_;Y#N    419     Hyšplerová_;Y#N 2153
      ```
    - někdy je to kvůli divnému propojení:
      ```
      Andrej_;Y#N     56507   Ondřej_;Y#N     301797
      Baníkov_;G#N    55      baníkovský#A    2836
      Hradišť_;G_^(rozhledna)#N       0       hradišťský#A    29750
      Ince_;Y#N       492     incký#A 1393
      ```
