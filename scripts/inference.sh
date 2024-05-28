#!/bin/bash

model_path= # path to the model, PATH2X-Instruction-7b-10langs
prompt= # prompt, e.g. "Give some tips on how to design a trip to New York."
output_lang= # output language, e.g. "Urdu"
cuda= # cuda device, e.g. "cuda:0"


python -u utils/inference.py \
    --model_path ${model_path} \
    --prompt ${prompt} \
    --output_lang ${output_lang} \
    --is_xIns \  
    --is_aug \  
    --cuda ${cuda}