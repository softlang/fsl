none:

pldb.json:
	curl -L https://pldb.io/pldb.json -o pldb.json

languages.json: pldb.json
	jq 'map({id: .id, name: .name, wikipedia: .wikipedia})' \
		pldb.json > languages.json

clean:
	rm -f pldb.json languages.json

