#!/usr/bin/env bash

rm -r meta/conll2012_en_gold
rm -r meta/semeval_ca_gold
rm -r meta/semeval_es_gold
rm -r meta/semeval_it_gold

rm -r log/conll2012_en_gold
rm -r log/semeval_ca_gold
rm -r log/semeval_es_gold
rm -r log/semeval_it_gold

rm -r evaluation/conll2012_en_gold.md
rm -r evaluation/semeval_ca_gold.md
rm -r evaluation/semeval_es_gold.md
rm -r evaluation/semeval_it_gold.md

rm -r evaluation/conll2012_en_gold
rm -r evaluation/semeval_ca_gold
rm -r evaluation/semeval_es_gold
rm -r evaluation/semeval_it_gold

python corefgraph/process/corpus.py -p experiments/conll2012/experiment_gold.yaml
python corefgraph/process/corpus.py -p experiments/semeval2010/it/experiment_v8_test_gold.yaml
python corefgraph/process/corpus.py -p experiments/semeval2010/es/experiment_v8_es_test_gold_final.yaml
python corefgraph/process/corpus.py -p experiments/semeval2010/ca/experiment_v8_test_gold_base.yaml
