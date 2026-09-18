java.json: Makefile
	jq '.[] | select(.id == "java")' \
		../../pldb.json > java.json

clean:
	rm -f *.json
