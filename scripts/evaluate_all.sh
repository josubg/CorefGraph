#!/usr/bin/env bash

./scripts/go.sh ./experiments/conll2012/experiment_official_open.yaml > CONLL2012.csv
./scripts/go_es.sh ./experiments/semeval2010/experiment_v8_es_test_predicted.yaml > semeval_es.csv

./scripts/go.sh ./experiments/meantime/experiment_official_en.yaml >meantime_en.csv
./scripts/go_es.sh ./experiments/meantime/experiment_official_es.yaml > meantime_es.csv


