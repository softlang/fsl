SCRIPT_DIR  := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
VENV        := $(SCRIPT_DIR)venv
PYTHON      := $(VENV)/bin/python
SAREF_DEV   := $(VENV)/bin/saref-dev
SAREF_CORE  := $(SCRIPT_DIR)saref-core-reference
VERSIONING  := $(SCRIPT_DIR)versioning
RESULTS     := $(SCRIPT_DIR)results/versioning

venv: $(VENV)/bin/python

$(VENV)/bin/python:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --quiet -r $(SCRIPT_DIR)requirements.txt

clone-saref-core:
	@if [ ! -d "$(SAREF_CORE)" ]; then \
	    git clone --depth=1 https://labs.etsi.org/rep/saref/saref-core.git $(SAREF_CORE); \
	else \
	    echo "saref-core already cloned."; \
	fi

check-saref-core: venv clone-saref-core
	@mkdir -p $(SCRIPT_DIR)results
	$(SAREF_DEV) check --skip-fetch $(SAREF_CORE) \
	    2>&1 | tee $(SCRIPT_DIR)results/saref-core-pypeline.md

check-fsl-main: venv
	@mkdir -p $(SCRIPT_DIR)results
	@git worktree add /tmp/fsl-main main 2>/dev/null || true
	$(PYTHON) $(SCRIPT_DIR)run_checks.py \
	    --ttl /tmp/fsl-main/ontologies/fsl.ttl \
	    --extra-ttl /tmp/fsl-main/ontologies/ \
	    --label "FSL-main" \
	    2>&1 | tee $(SCRIPT_DIR)results/fsl-main-check.md; \
	git worktree remove /tmp/fsl-main 2>/dev/null; true

check-fsl-exp: venv
	@mkdir -p $(SCRIPT_DIR)results
	$(PYTHON) $(SCRIPT_DIR)run_checks.py \
	    --ttl $(SCRIPT_DIR)../ontologies/fsl.ttl \
	    --extra-ttl $(SCRIPT_DIR)../ontologies/ \
	    --label "FSL-exp" \
	    2>&1 | tee $(SCRIPT_DIR)results/fsl-exp-check.md

versioning-layout:
	@mkdir -p $(RESULTS)/batches $(RESULTS)/llm-output $(RESULTS)/candidate-patches $(RESULTS)/validation $(RESULTS)/evaluation
	@echo "Versioning results directory is ready: $(RESULTS)"

versioning-request: venv versioning-layout
	$(PYTHON) $(VERSIONING)/scripts/build_batch_request.py \
	    --evidence $(VERSIONING)/src/python-3.13.json \
	    --prompt $(VERSIONING)/prompts/system.md \
	    --schema $(VERSIONING)/schemas/version-addition-response.schema.json \
	    --output $(RESULTS)/batches/python-3.13.jsonl

versioning-run: venv versioning-layout
	$(PYTHON) $(VERSIONING)/scripts/run_batch_request.py \
	    --batch $(RESULTS)/batches/python-3.13.jsonl \
	    --out-dir $(RESULTS)/llm-output \
	    $(if $(MOCK),--mock-response $(VERSIONING)/scripts/fixtures/python-3.13.response.json,)

versioning-validate: venv versioning-layout
	$(PYTHON) $(VERSIONING)/scripts/render_and_validate.py \
	    --evidence $(VERSIONING)/src/python-3.13.json \
	    --response $(RESULTS)/llm-output/python-3.13.json

versioning-pr: venv
	$(PYTHON) $(VERSIONING)/scripts/open_pr.py \
	    --evidence $(VERSIONING)/src/python-3.13.json \
	    $(if $(PR),--create-pr,$(if $(PUSH),--push,))

versioning-detect: venv
	@mkdir -p $(RESULTS)/detected
	$(PYTHON) $(VERSIONING)/scripts/detect_new_releases.py $(EXTRA)

check-all: check-fsl-main check-fsl-exp

clean:
	rm -rf $(SCRIPT_DIR)results/
	rm -rf $(SAREF_CORE)
	@git worktree remove /tmp/fsl-main 2>/dev/null; true

.PHONY: venv clone-saref-core check-saref-core check-fsl-main check-fsl-exp versioning-layout versioning-request versioning-run versioning-validate versioning-pr versioning-detect check-all clean
