#########################################################################
########################## Local Dev Tools ##############################
#########################################################################
run-test:
	( \
		. .venv/bin/activate; \
		pytest -sv --cov-report=xml; \
	)
run-coverage:
	( \
		. .venv/bin/activate; \
		coverage run --source=src -m pytest; \
	)
generate-snapshot:
	( \
		. .venv/bin/activate; \
		pytest --snapshot-update; \
	)

lint:
	( \
		. .venv/bin/activate; \
		./scripts/lint.sh; \
	)

format: ./scripts/format.sh