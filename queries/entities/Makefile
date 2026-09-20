export PYTHONPATH := ../../utils:$(PYTHONPATH)

all:
	python3 summary.py
	make contexts
	make wikipedia_links.json

wikipedia_links.json: wikipedia_links.py ../../ontologies/*.ttl
	python3 wikipedia_links.py
	
contexts: contexts.py ../../ontologies/*.ttl
	rm -rf contexts
	mkdir contexts
	python3 contexts.py

clean:
	gm -f *.csv
	rm -rf contexts
