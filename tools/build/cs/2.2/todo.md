Anotace do DeriNetu před verzí 2.2
=============================

Release 2.1.x
-----------------

[ZŽ+MŠ+LK+JV, otevřené]
Univerbizace. MŠ a ZŽ mají manuálně anotovaná a pročištěná data univerbátů.
Jedná se o vztahu typu "minerál+ka < minerální voda", v některých koncepcích
ale také "hovězí.A < hovězí maso". Je potřeba postzprocesovat data a rozhodnout,
jak chceme univerbizaci zachycovat, např.
(i) jako Type="Derivation" ale se dvěma linky, což může být komplikované
technicky (API předpokládá, že derivace má jednoho rodiče), nebo
(ii) nový typ relace Type="Univerbization" mající dva linky.
