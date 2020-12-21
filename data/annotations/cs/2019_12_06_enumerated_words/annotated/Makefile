.PHONY: all clean

.SUFFIXES:
.SUFFIXES: .tsv .xlsx .ods

all: vyjmenovana-slova-sd.tsv vyjmenovana-slova-sd-jv.tsv

.xlsx.tsv:
	libreoffice --headless --convert-to csv:'Text - txt - csv (StarCalc)':9,34,UTF8 '$<' && mv '$*.csv' '$*.tsv'

.ods.tsv:
	libreoffice --headless --convert-to csv:'Text - txt - csv (StarCalc)':9,34,UTF8 '$<' && mv '$*.csv' '$*.tsv'

clean:
	rm -f vyjmenovana-slova-sd.tsv vyjmenovana-slova-sd-jv.tsv
