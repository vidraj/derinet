Další anotace do DeriNetu 2.1
=============================

Nějak jsou hotové / zpracovávají se
-----------------

(Ne)motivovanost nejfrekventovanějích stromových kořenů (je v adresáři
2019_01_freq_roots, přesune se do 2020_01_motivation_of_tree_root_nodes).
Anotace má Lukáš (ze srpna 2019 a ledna 2020). Skript napíše Lukáš, Zdeněk
zkontroluje data, chce dalších 20000 řádků (od Šárky je anotovaných 6000).
Přidat bit stromovým kořenům, které jsou skutečně potvrzeně nemotivované,
přidat rodiče stromovým kořenům, které jsou motivované, přidat compound=True
stromovým kořenům, které jsou kompozitem.

Frekvence z korpusu. Máme absolutní frekvence, ale je potřeba dodělat další
skóre na jejich základě, viz e-mail od Zdeňka z března 2020.
Jmenovatel relativní frekvence by měla být velikost korpusu včetně čárek,
zájmen etc. Ale u kumulativní četnosti je jmenovatelem jenom počet slov
v DeriNetu. Zpracuje Jonáš; TODO tohle ještě probrat se Zdeňkem.

Slovesné třídy (2020_07_conjugation_class). Vezmou se z Lukášova
nástroje. Skript napíše Lukáš. Nechají se i přechody mezi třídami. Pro slovesa,
u kterých nástroj nedokáže určit třídu, nebude třída vyplněna.
Značka se vloží do JSON sloupce jako "conjug_class".

Přechod na nový MorfFlex. Vezmeme aktuální verzi z Gitu a uvidíme, jestli to
bude průchozí. Zpracuje Jonáš.

Vyjmenovaná slova (2019_12_06_enumerated_words). Smazat z výstupu počáteční
vy- a vý-, udělat z toho XLS soubor, kde se zaznačí předek, kompozitnost nebo
značka, že je to správně. Poslat rovnou Šárce (posláno 2020-07-10). Zpracovává
Jonáš.

Značka cizosti (2020_03_loanwords). Pomocí Lukášova pravidlového
nástroje se každému lemmatu dala do JSON sloupce značka "loanword=True/False".
Prodiskutovat by se mělo: dědičnost příznaku, zda určovat u vlastních jmen. (?)



Čekají a vhodný okamžik
-----------------

Segmentace. Vezmeme od pana Bodnára, až v půlce července odevzdá diplomku.
Jinak se různé manuální segmentace (kořenů) vyskytují v adresáři
2020_01_root_allomorphs_cleanup (hotovo v DeriNetu 2.0). Lukáš a Magda má také
poloautomaticky odsegmentované a ručně zkontrolované předpony u sloves.

Varianty. Anša Vernerová posílala 20. 9. 2019 e-mail se slovesnými variantami.
Ty by se daly přilít, označit pomocí sémantického labelu a pro každé hnízdo
variant (např. extremismus, extrémismus, extremizmus, extrémizmus) zvolit jedno
základní a ostatní pověsit přímo na něj. Takže citronový by viselo na citrónový,
ne na citron, a mělo by značku pro variantu.
Asi se tomu bude věnovat pan Bodnár v rámci nějakého DPP nebo SFG.
Jak je vytáhnout? Seznam známých typů změn profiltrovat třeba přes překladové
ekvivalenty, aby se vyloučila kosa/koza etc.
Jonáš se podívá, jak jsou varianty řešeny v současném Gitu MorfFlexu.



Nejsou, ale chtěli bychom
-------------------------

K četnostem: Podívat se, kolik stromů se rozpadne, protože mají uprostřed slovo
bez korpusových výskytů.
Zkontrolovat stromy, jestli sedí sestupnost frekvencí. Někde to určitě nebude
sedět z dobrých lingvistických důvodů, ale jinde z toho můžeme dostat podezřelé
kandidáty.
