#!/bin/bash

LANGUAGES= # array of languages, e.g. ("fi")

max_tokens= # max tokens for generation, e.g. 512
temperature= # temperature for generation, e.g. 0
top_p= # top-p for generation, e.g. 1.0

question_file_path= # path to input question file, e.g. ./data/vicuna-eval/fi/question.jsonl
answer1_file_path= # path to first answer file, e.g. ./data/vicuna-eval/fi/answer.fi.xInstruct.eval.jsonl
answer2_file_path= # path to second answer file, e.g. ./data/vicuna-eval/fi/answer.fi.chatgpt.eval.jsonl
output_path= # path to output directory, e.g. ./eval/vicuna-eval/fi/
start_idx= # start index for evaluation, e.g. 0


for lang in "${LANGUAGES[@]}";do
    # answer1_file_path vs answer2_file_path
    python -u utils/gpt4_eval.py \
        --max-tokens $max_tokens \
        --temperature $temperature\
        --top-p $top_p \
        --lang $lang \
        --question_file_path $question_file_path \
        --answer1_file_path $answer1_file_path \
        --answer2_file_path $answer2_file_path \
        --output_path $output_path \
        --start_idx $start_idx \
        --debug 
    done

    # answer2_file_path vs answer1_file_path
    python -u utils/gpt4_eval.py \
        --max-tokens $max_tokens \
        --temperature $temperature\
        --top-p $top_p \
        --lang $lang \
        --question_file_path $question_file_path \
        --answer1_file_path $answer2_file_path \
        --answer2_file_path $answer1_file_path \
        --output_path $output_path \
        --start_idx $start_idx \
        --debug 
    done
done



