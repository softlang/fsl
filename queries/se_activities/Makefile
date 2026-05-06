all:
	make instances.run
	make immediate_subclasses.run
	make nonimmediate_subclasses.run
	make used_nonimmediate_subclasses.run
	make unused_nonimmediate_subclasses.run
	make nonimmediate_subclass_properties.run
	python3 summary.py

summary.csv: *.log summary.py
	python3 summary.py

%.run:
	python3 $*.py > $*.log

clean:
	rm -f *.log *.csv
