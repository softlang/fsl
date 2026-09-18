export PYTHONPATH := ../../utils:$(PYTHONPATH)

all:
	make instances.run
	make immediate_subclasses.run
	make nonimmediate_subclasses.run
	make used_immediate_subclasses.run
	make used_nonimmediate_subclasses.run
	make properties.run
	make language_instances.run
	make language_subclasses.run
	make tool_instances.run
	make tool_subclasses.run
	make artifacts.run
	python3 summary.py

summary.csv: *.log summary.py
	python3 summary.py

%.run:
	python3 $*.py > $*.log

clean:
	rm -f *.log *.csv
