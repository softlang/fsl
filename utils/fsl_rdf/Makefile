none:

install:
	python3 -m pip install "rdflib>=7.1,<8"
	python3 -m pip install "pytest>=8,<10"

roundtrip:
	rm -rf build
	python3 fsl_rdf.py ../../ontologies build/ontologies
	cp ../../ontologies/*.xml build/ontologies
	cp ../../ontologies/*.csv build/ontologies

test:
	python3 -m pytest -v test_fsl_rdf.py

clean:
	rm -rf build
