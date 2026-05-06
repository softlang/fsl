all:
	make instances.run
	make subclasses.run
	make spaces_with_languages.run
	make languages_with_spaces.run
	make spaces_with_tools.run
	make tools_with_spaces.run
	make spaces_with_artifacts.run
	make artifacts_with_spaces.run
	python3 summary.py

summary.csv: *.log summary.py
	python3 summary.py

%.run:
	python3 $*.py > $*.log

clean:
	rm -f *.log *.csv
