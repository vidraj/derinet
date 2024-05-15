
          ███████          ███████          ██      █  ███████████
          █     █          █     █          ██      █       █
          █     █          █     █          █ ██    █       █
          █    █           █    █           █   █   █       █
          ██████           ██████           █   █   █       █
          █       ████     █  █      ███    █    ██ █       █
          █           █    █   █    █   █   █     █ █       █
          █       █████    █    █   █████   █      ██       █
          █      █    █    █    █   █       █      ██       █
          █       ████ █   █     █   ████   █       █       █
         ┏━━┓     ┏━━┓      ┏━━┓     ┏━━┓      ┏━━┓       ┏━━┓
         ┃  ┠┐    ┃  ┠┐     ┃  ┠─┐  ┌┨  ┃ ┌────┨  ┃      ┌┨  ┃
         ┗┯┯┛│    ┗┯┯┛│     ┗┯┯┛ │  │┗┯┯┛ │    ┗┯┯┛      │┗┯┯┛
          ││ │     ││ │  ┌───┘│╔═╪══╩═╪╪══╪═════╩┼───────┘ ││
          ││ └─────┼┼─╧══╪════╩╬═╪════╬╩══╪══╗  ┌┘         ││
          │└───────┼╧════╪═════╬╗│   ╔╝   ╠──╫──┼──────────┘│
          │        │    ┏┷━┓   ║║│ ┏━┷┓   ║  ║┏━┷┓          │
          └────────╧════┨  ┠═══╝╚╧═┨  ┠═══╝  ╚┨  ┠──────────┘
                        ┗┯┯┛       ┗┯┯┛       ┗┯┯┛
                 ┌───────┘│╔════════╧┼─────────┤└───────┐
                 │        └╫───┬─────┼─────────┼─────┐  │
                 │  ╔══════╝   │  ┌──┴────┐    │     │  │
                 │  ║          │  ╠───────┼──┬─┘     │  │
                 │  ║          │  ║       │  │       │  │
                 └┏┓╝          └┏┓╝       └┏┓┘       └┏┓┘
                  ┗┛            ┗┛         ┗┛         ┗┛
                Parent       Retrieval   Neural      Tool


Skript roots_only.py vytvoří soubor false_roots.tsv všech kořenů v DeriNetu seřazený podle toho, jak PaReNT považuje
za pravděpodobné, že se nejedná o nemotivované slovo. Skript defaultně neukládá vlastní jména nekončící
na "á", protože jinak PaReNT provádí paskvil typu Kněz -> Kněžík. Jinak dopočítává Bednářová -> Bednář,
což bývá správně. Pokud si toto chování uživatel nepřeje, stačí filtr zakomentovat.

Soubor má následující sloupce:

'lemma'                             :           Lemma vstupního lexému.
'Correct_candidate'                 :           Index kandidáta ze sloupce PaReNT_retrieval_candidates, který je správný.
                                                *Defaultně je 0, doporučuji při anotaci editovat tento sloupec.*
                                                Jestli je nultý/první kandidát špatně, pravdpodobně je v seznamu i
                                                správný kandidát.
'PaReNT_retrieval_candidates'       :           Seznam kandidátů predikovaných PaReNTem.
'PaReNT_classification'             :           Argmax napříč třemi posledními sloupci.
'PaReNT_Compound_probability'       :           Pravděpodobnost, že jde o kompozitum.
'PaReNT_Derivative_probability'     :           Pravděpodobnost, že jde o derivát.
'PaReNT_Unmotivated_probability'    :           Pravděpodobnost, že jde o nemotivované slovo.