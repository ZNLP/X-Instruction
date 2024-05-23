#!/bin/bash
LANGUAGES= # array of languages, e.g. ("bn")
input_file= # path to input question file, e.g. ./data/vicuna-eval/bn/question.jsonl

for lang in "${LANGUAGES[@]}";do
    python -u utils/chatgpt_generation.py \
    --input_file ${input_file} \
    --lang ${lang}
done