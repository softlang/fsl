java.json: Makefile
	jq '.[] | select(.id == "java") | with_entries( select((.value | tostring | length) < 500))' \
		../../pldb.json > java.json

clean:
	rm -f *.json
