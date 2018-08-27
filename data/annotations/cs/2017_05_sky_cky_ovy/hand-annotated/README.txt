Adélin komentář z mejlu k kandidati_ze_sirotku:

prošla jsem ta slova, která jsem automaticky vyřadila jako kompozita,
a zkontrolovala, jestli se o kompozita opravdu jedná. Pokud ne,
napsala jsem před celý řádek N<tab>. V takovýchto případech jsem se
také pokusila rovnou specifikovat základové slovo - tento údaj je na
konci řádku ve formátu A:slovo. Pokud jsem nevěděla, jak s daným
slovem naložit, připsala jsem na začátek ?<tab>, případné komentáře
jsou ve formátu ###(komentář)###. Řádky, které na začátku nemají N ani
?, by měly obsahovat kompozita.


Zdeněk:

soubory candidates_cky_bez_kompozit.txt, candidates_ovy_bez_kompozit.txt
a candidates_sky_bez_kompozit.txt jsem anotoval takhle:

- řádky, kde jsem s predikovaným předkem nesouhlasil, ale neměl jsem lepší
návrh, jsem označil otazníkem na začátku řádku, např. 
?horenský horna	    CHANGE: rna --> renský
?	fyzický	fyzik	CHANGE: k --> ck

- na řádcích, kde nebyl predikovaný žádný předek, nebo byl predikovaný
  chybný předek, jsem na konec řádku přidal Z: lemmapředka
  např. městský	městsko	CHANGE: sko --> ský Z: město
  (v mnoha případech šlo jen o změnu malého písmena na velké)
  téměř vždy byla předkem substantiva


Magda:
- na řádcích, kde nebyl predikovaný žádný předek, nebo byl predikovaný
  chybný předek, jsem na konec řádku přidala M: lemmapředka
  např.
  N černosotěnský		UNRESOLVED A:černosotněnec
  jsem změnila na
  N černosotěnský		UNRESOLVED M:černosotěnec
