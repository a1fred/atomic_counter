# Atomic counter as a service
* Rest api
* Persisted
* Multiple counters supported


## Run
python -m atomic_counter --datadir=./data

## Get counters
GET /

## Increment and get value
GET /<counter_name>

# Just get counter value
HEAD /<counter_name>
