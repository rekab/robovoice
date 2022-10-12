#!/bin/bash
SRC_DIR=$(dirname $0)

while $SRC_DIR/run.sh ; do
  sleep 1
  echo "retrying"
done
