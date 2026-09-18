export PYTHONPATH := ../../utils:$(PYTHONPATH)

all:
	cd ../../ontologies/versions; make
	python3 categorization.py

clean:
	rm -f *.csv *.png
