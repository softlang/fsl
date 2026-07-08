all:
	make version_sequence.run
	make successor_chain.run
	make cross_entity_versions.run
	make language_tool_pairing.run
	python3 summary.py

summary.csv: *.log summary.py
	python3 summary.py

%.run:
	python3 $*.py > $*.log

clean:
	rm -f *.log *.csv
