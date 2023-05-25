#########################################################################
########################## Local Dev Tools ##############################
#########################################################################
run-test:
	( \
		export $$(grep -v '^#' ./envs/.env.test | xargs); \
		. .venv/bin/activate; \
		pytest -sv --cov-report=xml; \
	)
run-coverage:
	( \
		export $$(grep -v '^#' ./envs/.env.test | xargs); \
		. .venv/bin/activate; \
		coverage run --source=src -m pytest; \
	)
generate-snapshot:
	( \
		export $$(grep -v '^#' ./envs/.env.test | xargs); \
		. .venv/bin/activate; \
		pytest --snapshot-update; \
	)

lint:
	( \
		export $$(grep -v '^#' ./envs/.env.test | xargs); \
		. .venv/bin/activate; \
		./scripts/lint.sh; \
	)

format:
	( \
		export $$(grep -v '^#' ./envs/.env.test | xargs); \
		. .venv/bin/activate; \
		./scripts/format.sh; \
	)
