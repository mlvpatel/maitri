.PHONY: install dev lint test eval demo deploy clean smoke

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -U pip && pip install -e ".[dev,rag]"

smoke:
	. .venv/bin/activate && python -m maitri.gemma_client --smoke

dev:
	. .venv/bin/activate && python app.py

lint:
	. .venv/bin/activate && ruff check src tests

test:
	. .venv/bin/activate && pytest

eval:
	. .venv/bin/activate && python -m eval.harness

demo:
	. .venv/bin/activate && python -m examples.case_2_verifier_rejects_hallucination

deploy:
	@echo "Run scripts/deploy_space.sh after confirming HF_TOKEN is set"

clean:
	rm -rf .venv .pytest_cache .ruff_cache build dist *.egg-info
	find . -name __pycache__ -type d -exec rm -rf {} +
