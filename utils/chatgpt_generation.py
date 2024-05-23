import argparse
from ast import parse
import json
import jsonlines
import os
import logging
import time
import openai
from tqdm import tqdm

import asyncio
from typing import Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


openai.api_key = "<YOUR OPENAI API KEY>"

# default setting
_CROSS_LINGUAL_PROMPT=(
     "Given an instruction in English, please generate a response in {lang}.\n\n"
     "Instruction: {instruction}\n\n"
     "### Response:"
)


# Mapping from language code to language name
_LANG_CODE_TO_NAME = {
    "en": "English",
    "zh": "Chinese",
    "ar": "Arabic",
    "th": "Thai",
    "tr": "Turkish",
    "hi": "Hindi",
    "id": "Indonesian",
    "fi": "Finnish",
    "bn": "Bengali",
    "vi": "Vietnamese",
    "ta": "Tamil",
    "te": "Telugu",
    "sw": "Swahili",
    "ur": "Urdu",
}

def read_jsonl(path:str):
    with open(path, "r", encoding="utf-8") as f:
        samples = [json.loads(l.strip()) for l in f.readlines()]
    return samples

def openai_requests(
    messages_list: list[list[dict[str,Any]]],
    model: str,
    temperature: float,
    max_tokens: int,
    top_p: float,
) -> list[str]:
    """
    Dispatches requests to OpenAI API.
    
    Args:
        messages_list: List of messages to be sent to OpenAI ChatCompletion API.
        model: OpenAI model to use.
        temperature: Temperature to use for the model.
        max_tokens: Maximum number of tokens to generate.
        top_p: Top p to use for the model.

    Returns:
        List of responses from OpenAI API.
    """
    
    async_responses = [
        openai.ChatCompletion.create(
            model=model,
            messages=x,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
        )
        for x in messages_list
    ]
    return async_responses



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ChatGPT-based QA evaluation.")
    parser.add_argument("-o", "--output-review-file")
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2048,
        help="maximum number of tokens produced in the output",
    )
    parser.add_argument(
        "-i",
        "--input_file",
        type=str,
        default="/home/wyang/work/XInstruct/data/vicuna-eval/sw/question.jsonl",
        help="the file to request the ChatGPT to rate"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-3.5-turbo",
        help="the model for automatic evaluation"
    )
    parser.add_argument(
        "--start_idx",
        type=int,
        default=0
    )
    parser.add_argument(
        "--save_num",
        type=int,
        default=1
    )
    parser.add_argument(
        "--lang",
        type=str,
        default="sw"
    )
    
    args = parser.parse_args()
    message_list = []
    dataset = read_jsonl(args.input_file)

    args.output_file = args.input_file.replace("question.jsonl", f"answer.{args.lang}.chatgpt.eval.jsonl")

    print(f"Data Num: {len(dataset)}")
    print(f"Start from: {args.start_idx}")

    for i in range(len(dataset)):
        if i < args.start_idx:
            continue

        system_prompt = "We would like to request your feedback on the performance of AI assistant in response to the instruction and the given input displayed following."
        
        eval_prompt = _CROSS_LINGUAL_PROMPT.format(
            lang = _LANG_CODE_TO_NAME[args.lang],
            instruction=dataset[i]["text"],
        )

        message =[
                   {"role": "system", "content": system_prompt},
                   {"role": "user", "content": eval_prompt},
        ]
        message_list.append(message)


    predictions = []
    i = 0
    wait_base = 1
    retry = 0
    pbar = tqdm(total=len(message_list))

    while(i<len(message_list)):
        predictions = openai_requests(
                                messages_list=message_list[i:i+1],
                                model=args.model,
                                temperature=0.7,
                                max_tokens=args.max_tokens,
                                top_p=1.0,
                                )
        print(f"\nidx=={i}, Saving the result...")

        for idx, prediction in tqdm(enumerate(predictions)):
            review = prediction['choices'][0]['message']['content']
            
            meta_output = dataset[i]
            meta_output.update({"output": review})          
        with open(f"{args.output_file}", "a") as output_file:
                output_file.write(json.dumps(meta_output, ensure_ascii=False) + '\n')
        i += 1
        wait_base = 1
        pbar.update(1)

    pbar.close()