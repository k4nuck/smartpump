#!/bin/bash

docker run -p 5984:5984 -d -v ~/.local/opt/couchdb/data:/opt/couchdb/data treehouses/couchdb:2.1.0
