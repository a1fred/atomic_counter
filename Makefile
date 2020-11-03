.PHONY: server
server:
	pipenv run python -m atomic_counter --datadir=./data
