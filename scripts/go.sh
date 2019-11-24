#!/usr/bin/env bash
filename=$(basename -- "$1")
filename="${filename%.*}"

mkdir -p log/${filename}
mkdir -p meta/${filename}

python -m corefgraph.process.corpus -p $1
