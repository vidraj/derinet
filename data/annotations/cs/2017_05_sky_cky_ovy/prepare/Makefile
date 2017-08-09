all: clone  run

clone:
	git clone https://github.com/tiefling-cat/derinet-python


run:
	export PYTHONPATH=$$PYTHONPATH:derinet-python && ./statistiky.py > log

stats:
	@echo "Uzlu celkem"
	@cat log | wc -l
	@echo
	@echo "S rodicem/bez rodice"
	@cat log | cut -f2 | sort | uniq -c | sort -nr
	@echo
	@echo "Male/velke prvni pismeno u sirotku"
	@cat log | grep BEZ_RODICE|cut -f3 | sort | uniq -c | sort -nr
	@echo
	@echo "Distribuce hloubky podstromu malopismennych sirotku"
	@cat log | grep MALE| grep BEZ_RODICE|cut -f6 | sort | uniq -c | sort -nr
	@echo
	@echo "Distribuce slovniho druhu malopismennych sirotku"
	@cat log | grep MALE| grep BEZ_RODICE|cut -f4 | sort | uniq -c | sort -nr
	@echo
	@echo "Distribuce delky lemmatu malopismennych sirotku"
	@cat log | grep MALE| grep BEZ_RODICE|cut -f5 | sort | uniq -c 
	@echo

retro:
	cat log | grep MALE | grep BEZ_RODICE | cut -f1 | rev | sort | rev > retro.txt
	cat log | grep MALE | grep BEZ_RODICE | cut -f1 | rev | perl -C -ne 's/(..).+/$$1/;print' | rev | sort | uniq -c | sort -nr > suffix2.txt
	cat log | grep MALE | grep BEZ_RODICE | cut -f1 | rev | perl -C -ne 's/(...).+/$$1/;print' | rev | sort | uniq -c | sort -nr > suffix3.txt
	cat log | grep MALE | grep BEZ_RODICE | cut -f1 | rev | perl -C -ne 's/(....).+/$$1/;print' | rev | sort | uniq -c | sort -nr > suffix4.txt


sky:
	./sky_candidates.py > candidates_sky.txt
	#export PYTHONPATH=$$PYTHONPATH:derinet-python && ./sky_candidates.py > candidates_sky.txt

ovy:
	export PYTHONPATH=$$PYTHONPATH:derinet-python && ./ovy_candidates.py > candidates_ovy.txt

cky:
	export PYTHONPATH=$$PYTHONPATH:derinet-python && ./cky_candidates.py > candidates_cky.txt
