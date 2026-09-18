export PYTHONPATH := ../../utils:$(PYTHONPATH)

all:
	make concepts.run
	make instances.run
	make classes.run
	make used_instances.run
	make used_classes.run
	make properties.run
	make annotated_sl_instances.run
	make annotated_pl_instances.run
	make annotated_sl_classes.run
	make annotated_pl_classes.run
	python3 summary.py

summary.csv: *.log summary.py
	python3 summary.py

%.run:
	python3 $*.py > $*.log

clean:
	rm -f *.log *.csv
