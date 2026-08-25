.PHONY: format format-check lint check-invariants check-brackets test

format:
	docker run --rm -v "$$(pwd):/workdir" -w /workdir node:20 npx --yes prettier@3.2.5 --write "**/*.{md,yml,yaml}"

format-check:
	docker run --rm -v "$$(pwd):/workdir" -w /workdir node:20 npx --yes prettier@3.2.5 --check "**/*.{md,yml,yaml}"

lint:
	docker run --rm -v "$$(pwd):/workdir" -w /workdir node:20 npx --yes markdownlint-cli2@0.13.0 "**/*.md" "#node_modules"

check-brackets:
	python3 scripts/check_brackets.py

check-invariants:
	python3 scripts/check_invariants.py

test: format-check lint check-invariants check-brackets
