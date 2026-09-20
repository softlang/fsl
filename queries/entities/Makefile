export PYTHONPATH := ../../utils:$(PYTHONPATH)

all:
	python3 summary.py
	make links.json
	make contexts

links.json: links.py
	python3 links.py

contexts: contexts.py ../../ontologies/*.ttl
	rm -rf contexts
	mkdir contexts
	python3 contexts.py

clean:
	gm -f *.csv
	rm -rf contexts
