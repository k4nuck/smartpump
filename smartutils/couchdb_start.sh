#!/bin/bash

docker run -p 5984:5984 -v /home/k4nuck/.local/opt/couchdb/data:/opt/couchdb/data -d --restart always couchdb:2.1
