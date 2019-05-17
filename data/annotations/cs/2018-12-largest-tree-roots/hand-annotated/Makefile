.PHONY: clean

sorted-trees-merged_MS_2019-02-17.csv: sorted-trees-merged_MS_2019-02-17.xlsx
	libreoffice --headless --convert-to csv:"Text - txt - csv (StarCalc)":9,34,UTF8 "$<"

pretnout-list.txt: sorted-trees-merged_MS_2019-02-17.csv
	 grep '^Manual.*\$$' "$<" > "$@"

clean:
	rm -f sorted-trees-merged_MS_2019-02-17.csv
	rm -f pretnout-list.txt
