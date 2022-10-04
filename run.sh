#!/bin/bash

SRC_DIR=$(dirname $0)

log() {
  echo "$0: " $(date +'%Y-%m-%d %H:%M:%S'): "$@"
}

log "starting"
source $SRC_DIR/voice-env/bin/activate

python3 $SRC_DIR/robovoice.py
