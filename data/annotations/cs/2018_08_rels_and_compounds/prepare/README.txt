VZTAHY
- manuálně nalezené nutné opravy


KOMPOZITA
1) make merge
comps1.txt
- původ příkazem: egrep "^[0-9]*.[^[:space:]]*ně[^[:space:]]{3,}.*[ADNV][^C]" derinet-1-5.tsv | grep -v 'něnost[[:space:]]' | grep -v 'něvší[[:space:]]' | less
- ručně anotováno (v souboru jsou už jen kompozita)

maillist.txt
- původ od Jonáše z mailu (v souboru jsou už jen kompozita)

comps2.txt
- původ příkazem: [lemma="^\p{Lowercase}.{10}" parent=="-1" pos!="C$"]
- ručně anotováno (v souboru jsou už jen kompozita)

2) make lexinfos
- sloučení souborů, setřídění, zunikátnění, nalezení "derinet_api.lexeme_info()" v derinetu
- uložení do souboru compounds.tsv
