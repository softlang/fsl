all:
	make instances.run
	make used_instances.run
	make unused_instances.run
	make instance_properties.run
	make subclasses.run
	make used_subclasses.run
	make unused_subclasses.run
	make subclass_properties.run
	python3 summary.py

summary.csv: *.log summary.py
	python3 summary.py

%.run:
	python3 $*.py > $*.log

clean:
	rm -f *.log *.csv
