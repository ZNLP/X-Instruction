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

import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


openai.api_key = "<YOUR OPENAI API KEY>"

'''
### Prompt_1, with outputing justification
_EVAL_PROMPT = (
    "Given the question in English, and the answer should be in {lang} language. You are a helpful and precise assistant for checking the quality of the answer in {lang}.\n\n"
    "<question>\n"
    "{instruction}\n"
    "</question>\n"
    "<answer1>\n"
    "{output1}\n"
    "</answer1>\n"
    "<answer2>\n"
    "{output2}\n"
    "</answer2>\n\n"
    "Suppose the user only speaks the language of the question, please evaluate both answers with your justification having less than three sentences, "
    "and provide a score ranging from 0 to 10 after your justifications. When evaluating the answers, you should consider the helpfulness, relevance, accuracy, "
    "level of details of the answers. The score for answer 1 should be wrapped by <score1> and </score1>, "
    "and the score for answer 2 should be wrapped by <score2> and </score2>.\n\n"
)
'''
### Prompt_2, without outputing justification
_EVAL_PROMPT = (
    "Given the question and the answer in {lang} language. You are a helpful and precise assistant for checking the quality of the answer in {lang}.\n\n"
    "<question>\n"
    "{instruction}\n"
    "</question>\n"
    "<answer1>\n"
    "{output1}\n"
    "</answer1>\n"
    "<answer2>\n"
    "{output2}\n"
    "</answer2>\n\n"
    "Suppose the user only speaks the language of the question, please evaluate both answers with your justification, "
    "and only provide a score ranging from 0 to 10 after your justifications, the score must be an integer. When evaluating the answers, you should consider the helpfulness, relevance, accuracy, "
    "level of details of the answers. The score for answer 1 should be wrapped by <score1> and </score1>, "
    "and the score for answer 2 should be wrapped by <score2> and </score2>.\n\n"
    "Please only output the scores for the answers, and do not output the justification and any other information.\n\n"
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

def extract_score(review: str) -> float:
    """
    Extracts the score from the review.

    Args:
        review: The review to extract the score from.

    Returns:
        The score.
    """
    match_1 = re.search('<score1>(.*?)</score1>', review)
    match_2 = re.search('<score2>(.*?)</score2>', review)

    if match_1:
        score_1 = int(float(match_1.group(1)))
    else:
        # raise ValueError("No score1 found in review.")
        score_1 = -1

    if match_2:
        score_2 = int(float(match_2.group(1)))
    else:
        # raise ValueError("No score2 found in review.")
        score_2 = -1


    return score_1, score_2

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
   
    # openai parameters
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=256,
        help="maximum number of tokens produced in the output",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="temperature to use for the model",
    )
    parser.add_argument(
        "--top-p",
        type=float,
        default=1.0,
        help="top p to use for the model",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4",
        help="the model for automatic evaluation"
    )

    # file path
    parser.add_argument(
        "--question_file_path",
        type=str,
        default="/home/wyang/work/XInstruct/data/vicuna-eval/bn/question.jsonl",
        help="the file to request the ChatGPT to rate"
    )
    parser.add_argument(
        "--answer1_file_path",
        type=str,
        default="/home/wyang/work/XInstruct/data/vicuna-eval/bn/answer.bn.aug.eval.jsonl",
        help="the file to request the ChatGPT to rate"
    )
    parser.add_argument(
        "--answer2_file_path",
        type=str,
        default="/home/wyang/work/XInstruct/data/vicuna-eval/bn/answer.bn.bx.eval.jsonl",
        help="the file to request the ChatGPT to rate"
    )

    parser.add_argument(
        "--start_idx",
        type=int,
        default=0
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default="/home/wyang/work/XInstruct/test/vicuna-eval/bn/"
    )
    parser.add_argument(
        "--lang",
        type=str,
        default="bn"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False
    )
    parser.add_argument(
        "--aug_max_output",
        action="store_true",
        default=False
    )
    
    args = parser.parse_args()
    message_list = []
    
    start_time = time.time()
    question = read_jsonl(args.question_file_path)
    answer1 = read_jsonl(args.answer1_file_path)
    answer2 = read_jsonl(args.answer2_file_path)

    answer1_name = os.path.basename(args.answer1_file_path).split(".")[2]
    answer2_name = os.path.basename(args.answer2_file_path).split(".")[2]

    args.output_file = os.path.join(args.output_path, f"gpt4.eval.{answer1_name}.{answer2_name}.aug-min-output.jsonl")
    
    if args.aug_max_output: 
        if "aug" in answer1_name and "output-1" in answer1[0]:
            args.output_file = os.path.join(args.output_path, f"gpt4.eval.{answer1_name}.{answer2_name}.aug-max-output.jsonl") 
        if "aug" in answer2_name and "output-1" in answer2[0]:
            args.output_file = os.path.join(args.output_path, f"gpt4.eval.{answer1_name}.{answer2_name}.aug-max-output.jsonl")
    
    if not os.path.exists(args.output_file):
        os.makedirs(os.path.dirname(args.output_file), exist_ok=True)  

    data_num = min(len(answer1), len(answer2))



    print(f"Data Num: {data_num}")
    print(f"Start from: {args.start_idx}")

    for i in range(data_num):
        if i < args.start_idx:
            continue

        if answer1[i]["question_id"] != answer2[i]["question_id"]:
            print(f"answer1[{i}] and answer2[{i}] are not matched.")
            exit()

        if args.aug_max_output:
            # Max Output Comparison
            if "aug" in answer1_name:
                output_1 = max([answer1[i]["output-1"], answer1[i]["output-2"], answer1[i]["output-3"]], key=len) if "output-1" in answer1[i] else answer1[i]["output"]
            else:
                output_1 = answer1[i]["output"]

            if "aug" in answer2_name:
                output_2 = max([answer2[i]["output-1"], answer2[i]["output-2"], answer2[i]["output-3"]], key=len) if "output-1" in answer2[i] else answer2[i]["output"]
            else:
                output_2 = answer2[i]["output"]
        else:
            # Min Output Comparison
            output_1 = min([answer1[i]["output-1"], answer1[i]["output-2"], answer1[i]["output-3"]], key=len) if "output-1" in answer1[i] else answer1[i]["output"]
            output_2 = min([answer2[i]["output-1"], answer2[i]["output-2"], answer2[i]["output-3"]], key=len) if "output-1" in answer2[i] else answer2[i]["output"]


        system_prompt = "We would like to request your feedback on the performance of AI assistant in response to the instruction and the given input displayed following."
        
        eval_prompt = _EVAL_PROMPT.format(
            lang=_LANG_CODE_TO_NAME[args.lang],
            instruction=question[i]["text"],
            output1=output_1,
            output2=output_2,
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

    if args.debug:
        with open(f"{args.output_file}", "a") as output_file:
            output_file.write(
                "answer1: " + str(answer1_name) + " " + "answer2: " + str(answer2_name) + '\n'
                "max_tokens: " + str(args.max_tokens) + " " + "temperture: " + str(args.temperature) + " " + "top_p: " + str(args.top_p) + '\n'
            )

    while(i<len(message_list)):
        predictions = openai_requests(
                                messages_list=message_list[i:i+1],
                                model=args.model,
                                temperature=args.temperature,
                                max_tokens=args.max_tokens,
                                top_p=args.top_p,
                                )
        idx = i + args.start_idx
        print(f"\nidx=={idx}, Saving the result...")

        if args.aug_max_output:
            # Max Output Comparison
            if "aug" in answer1_name:
                output_1 = max([answer1[idx]["output-1"], answer1[idx]["output-2"], answer1[idx]["output-3"]], key=len) if "output-1" in answer1[idx] else answer1[idx]["output"]
            else:
                output_1 = answer1[idx]["output"]

            if "aug" in answer2_name:
                output_2 = max([answer2[idx]["output-1"], answer2[idx]["output-2"], answer2[idx]["output-3"]], key=len) if "output-1" in answer2[idx] else answer2[idx]["output"]
            else:
                output_2 = answer2[idx]["output"]
        else:
            # Min Output Comparison
            output_1 = min([answer1[idx]["output-1"], answer1[idx]["output-2"], answer1[idx]["output-3"]], key=len) if "output-1" in answer1[idx] else answer1[idx]["output"]
            output_2 = min([answer2[idx]["output-1"], answer2[idx]["output-2"], answer2[idx]["output-3"]], key=len) if "output-1" in answer2[idx] else answer2[idx]["output"]
        
        for k, prediction in tqdm(enumerate(predictions)):
            review = prediction['choices'][0]['message']['content']
        
            score_1, score_2 = extract_score(review)
            meta_output = {
                "question_id": answer1[idx]['question_id'], 
                "category": answer1[idx]['category'] if 'category' in answer1[idx] else answer2[idx]['category'],
                "score_1": score_1,
                "score_2": score_2,
                "gpt4_eval": review,
                "answer1": output_1,
                "answer2": output_2,
            }

            with open(f"{args.output_file}", "a") as output_file:
                    output_file.write(
                        json.dumps(meta_output, ensure_ascii=False) + '\n'
                    )
            
        i += 1
        wait_base = 1
        pbar.update(1)

    pbar.close()

    print(f"Time: {time.time()-start_time}")