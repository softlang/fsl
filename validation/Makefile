master = ../ontologies

all: all-tbox all-abox

all-tbox:
	make ClassDeclarationsMustHaveCommentShape.tbox
	make ClassDeclarationsMustHaveFoafLinkShape.tbox

all-abox:
	make TechnologySpacesMustBeSpecifiedShape.abox
	make TechnologySpacesMustHaveConformsToShape.abox

%.tbox:
%.tbox:
	@python3 -m pyshacl \
	  -s $(master)/tbox.ttl \
	  -e $(master)/ae.ttl \
	  $*.ttl > $*.log
	@if grep -q "Severity: sh:Violation" $*.log; then \
	  echo "❌ TBOX validation failed for $*"; \
	  exit 1; \
	else \
	  echo "✅ TBOX valid: $*"; \
	fi
%.abox:
	@python3 -m pyshacl \
	  -a \
	  -s $*.ttl \
	  -e $(master)/tbox.ttl \
	  -i owlrl \
	  -im \
	  $(master)/ae.ttl \
	  $(master)/ce.ttl \
	  $(master)/fe.ttl \
	  > $*.log
	@if grep -q "Severity: sh:Violation" $*.log; then \
	  echo "❌ ABOX validation failed for $*"; \
	  exit 1; \
	else \
	  echo "✅ ABOX valid: $*"; \
	fi
