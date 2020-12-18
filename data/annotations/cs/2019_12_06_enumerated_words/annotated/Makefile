.PHONY: all clean

.SUFFIXES:
.SUFFIXES: .tsv .xlsx

all: vyjmenovana-slova-sd.tsv

.xlsx.tsv:
	libreoffice --headless --convert-to csv:'Text - txt - csv (StarCalc)':9,34,UTF8 '$<' && mv '$*.csv' '$*.tsv'

clean:
	rm -f vyjmenovana-slova-sd.tsv
