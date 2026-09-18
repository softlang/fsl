none:

pldb.json:
	curl -L https://pldb.io/pldb.json -o pldb.json

languages.json: pldb.json
	jq 'map({id: .id, name: .name, wikipedia: .wikipedia})' \
		pldb.json > languages.json

matches.csv: matches.py languages.json
	python3 matches.py

clean:
	rm -f pldb.json languages.json

