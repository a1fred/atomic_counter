# Atomic counter as a service
* Rest api
* Persisted
* Multiple counters supported


## Run
make server

## Get counters
GET /

## Increment and get value
GET /<counter_name>

# Just get counter value
HEAD /<counter_name>
