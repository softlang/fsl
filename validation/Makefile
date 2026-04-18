master = ../ontologies

all:
	make all-tbox
	make all-abox

all-tbox:
	make ClassDeclarationsMustHaveCommentShape.tbox
	make ClassDeclarationsMustHaveFoafLinkShape.tbox
	make PropertyDeclarationsMustHaveCommentShape.tbox
	make PropertyDeclarationsMustHaveFoafLinkShape.tbox

all-abox:
	make TechnologySpacesMustBeSpecifiedShape.abox
	make TechnologySpacesMustHaveConformsToShape.abox
	make MetamodelingShapes.abox
	make EngineeringActivitiesMustBeSpecifiedShape.abox
	make MethodologicalApproachesMustBeSpecifiedShape.abox

# Checking annotations on tbox only works reliably with consuming it as the main graph
%.tbox:
	-@python3 -m pyshacl \
	  -s $*.ttl \
	  ${master}/tbox.ttl \
	  > $*.log
	@grep "Severity: sh:Violation" $*.log | wc -l

%.abox:
	-@python3 -m pyshacl \
	  -a \
	  -s $*.ttl \
	  -e ${master}/tbox.ttl \
	  -i owlrl \
	  -im \
	  ${master}/ae.ttl \
	  ${master}/ce.ttl \
	  ${master}/fe.ttl \
	  ${master}/ie.ttl \
	  ${master}/le.ttl \
	  ${master}/pe.ttl \
	  ${master}/te.ttl \
	  > $*.log
	@grep "Severity: sh:Violation" $*.log | wc -l
