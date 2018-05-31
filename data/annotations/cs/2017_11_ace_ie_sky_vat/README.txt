Anotace všech slov, která končí na uvedené kombinace písmen a neměla v DeriNetu
rodiče.

FORMÁT
======

Stejný jako v DeriNetu, tedy ID<tab>lemma<tab>techlemma<tab>POS<tab>parentID,
navíc jsou přidány 1-2 sloupečky pro lemma rodiče a techlemma rodiče
(v některých souborech jen lemma, jinde i techlemma podle toho, jak moc je
u daného zakončení podoba techlemmatu důležitá). Např.:

79	aarhuský	aarhuský_;G_^(Aarhuská_úmluva)	A	77	Aarhus	Aarhus_;G

Pokud se mi nepodařilo najít v DeriNetu vhodného rodiče a zároveň jsem ho byla
schopna najít jinde (buď vím, jaký má být, nebo jsem ho vygooglila), je tento
rodič uveden v 5. sloupci a označen <<<>>>, řádek pak vypadá např. takto:

5369	ajurvédský	ajurvédský	A	<<<ajurvéda>>>

Pokud se mi nepodařilo rodiče najít a ani Google si nevěděl rady, ale myslím si,
že by nějaký rodič existovat měl, značila jsem to <<<?>>>, opět v 5. sloupci:

5663	akdžakajský	akdžakajský	A	<<<?>>>

Pokud se mi nepodařilo najít rodiče, ale našla jsem jiné potenciální základové
slovo, které je dostatečně podobné, aby se mohlo jednat o chybu, zapsala jsem
do 5. sloupce <<<preklep>>>, např.:

1971	ackionářský	ackionářský	A	<<<preklep>>>

Slova, která podle mě odvozená nejsou (tj. značková a přejatá), mají 5. sloupec
volný:

509	abdikovat	abdikovat_:T	V

Kromě těchto slov mají 5. sloupec volný i kompozita, ta jsou klasicky značena
přidáním C k označení slovního druhu:

2400	addisabebský	addisabebský	AC
