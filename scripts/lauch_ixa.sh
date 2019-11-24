#!/usr/bin/env bash
IXA_PIPE_POS_HOME=../resources/ixa-pipe-pos
IXA_PIPE_POS_MODELS=${IXA_PIPE_POS_HOME}/morph-models-1.5.0

java -jar ${IXA_PIPE_POS_HOME}/target/ixa-pipe-pos-1.5.1-exec.jar server -l es --port 1337 -m ${IXA_PIPE_POS_MODELS}/es/es-pos-perceptron-autodict01-ancora-2.0.bin -lm ${IXA_PIPE_POS_MODELS}/es/es-lemma-perceptron-ancora-2.0.bin


