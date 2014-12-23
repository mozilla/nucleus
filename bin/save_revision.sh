#!/bin/bash

STATIC_DIR=nucleus/base/static
REVISION_FILE=$STATIC_DIR/revision.txt
PREV_REVISION_FILE=$STATIC_DIR/prev-revision.txt


if [ -f $REVISION_FILE ]; then
    mv $REVISION_FILE $PREV_REVISION_FILE
fi

git rev-parse HEAD > $REVISION_FILE
