.PHONY: languages
.PHONY: links

export PYTHONPATH := ../../utils:$(PYTHONPATH)

all:
	make languages
	make links

languages:
	python3 languages.py

links:
	python3 links.py

clean:
	rm -rf links
