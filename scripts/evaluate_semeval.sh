#!/usr/bin/env bash

rm -r log
mkdir log
./scripts/lauch_ixa.sh >log/ixa-pos.log 2>log/ixa-pos.error.log &

PREDICTED_WITH_SINGLETONS=../resources/conll-scorer/v8.01/buff.res.conll.coref_S_All_UN_head_semeval_rules_PPredicative_PAppositive_features_multiword_ME_BF_CE_BF_FRelative_FSameHeadConll_FBareNP_CatchersPermissive_V8_CorpusTest

PREDICTED_WITHOUT_SINGLETONS=../resources/conll-scorer/v8.01/buff.res.conll.coref_S_All_UN_head_semeval_rules_Singleton_PPredicative_PAppositive_features_multiword_ME_BF_CE_BF_FRelative_FSameHeadConll_FBareNP_CatchersPermissive_V8_CorpusTestNS

GOLD_WITH_SINGLETONS=../resources/conll-scorer/v8.01/buff.res.conll.coref_S_All_UN_head_semeval_rules_PurgesNo_features_multiword_ME_BF_CE_BF_F_No_GoldMentions_V8_CorpusTest

GOLD_WITHOUT_SINGLETONS=../resources/conll-scorer/v8.01/buff.res.conll.coref_S_All_UN_head_semeval_rules_PurgesNo_features_multiword_ME_BF_CE_BF_F_No_GoldNSMentions_V8_CorpusTestNS


export IXA_POS_PID=$!
export PYTHONPATH=${PYTHONPATH}:../resources/pycorpus:../resources/pynaf

rm ${PREDICTED_WITH_SINGLETONS}
rm ${PREDICTED_WITHOUT_SINGLETONS}
rm ${GOLD_WITH_SINGLETONS}
rm ${GOLD_WITHOUT_SINGLETONS}

./scripts/go.sh ./experiments/semeval2010/experiment_v8_es_test_predicted_final.yaml
cp ${PREDICTED_WITH_SINGLETONS} results/semeval2010_es_corefgraph_predicted_with_singletons.conll

./scripts/go.sh ./experiments/semeval2010/experiment_v8_es_test_predicted_final_no_singletons.yaml
cp ${PREDICTED_WITHOUT_SINGLETONS} results/semeval2010_es_corefgraph_predicted_no_sinlgetons.conll

./scripts/go.sh ./experiments/semeval2010/experiment_v8_es_test_gold_final.yaml
cp ${GOLD_WITH_SINGLETONS} results/semeval2010_es_corefgraph_gold_mentions_with_singletons.conll

./scripts/go.sh ./experiments/semeval2010/experiment_v8_es_test_gold_final_no_singletons.yaml
cp ${GOLD_WITHOUT_SINGLETONS} results/semeval2010_es_corefgraph_gold_mentions_no_singletons.conll


kill ${IXA_POS_PID}