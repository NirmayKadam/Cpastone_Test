PYTHON ?= python

.PHONY: verify tree

verify:
	$(PYTHON) scripts/verify_phase1.py

tree:
	rg --files --hidden -g '!node_modules' -g '!dist' -g '!build'
