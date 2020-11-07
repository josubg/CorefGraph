#!/usr/bin/env bash

echo "Catalan"
#python corefgraph/process/corpus.py -p experiments/semeval2010/ca/experiment_v8_test_gold.yaml
python corefgraph/process/corpus.py -p experiments/semeval2010/ca/experiment_v8_test_predicted.yaml
python corefgraph/process/corpus.py -p experiments/semeval2010/ca/experiment_v8_train_predicted.yaml


echo "italiano"
#python corefgraph/process/corpus.py -p experiments/semeval2010/it/experiment_v8_test_gold.yaml
python corefgraph/process/corpus.py -p experiments/semeval2010/it/experiment_v8_test_predicted.yaml
python corefgraph/process/corpus.py -p experiments/semeval2010/it/experiment_v8_train_predicted.yaml

echo "Español"
#python corefgraph/process/corpus.py -p experiments/semeval2010/es/experiment_v8_test_gold.yaml
python corefgraph/process/corpus.py -p experiments/semeval2010/es/experiment_v8_test_predicted.yaml
python corefgraph/process/corpus.py -p experiments/semeval2010/es/experiment_v8_train_predicted.yaml
