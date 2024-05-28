from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import json

PROMPT_DICT = {
    # xResponse with "Answer in Lang"
    "xres_prompt_no_input": (
        "Below is an instruction that describes a task. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n{instruction} Answer in {output_lang}. \n\n### Response:"
    ),

    # xResponse with "Answer in Lang and the style of an AI assistant."
    "xres_aug_prompt_no_input": (
        "Below is an instruction that describes a task. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n{instruction} Answer in {output_lang} and the style of an AI assistant. \n\n### Response:"
    ),

    # xInstruct without "Answer in Lang"
    "xins_prompt_no_input": (
        "Below is a text that describes a candidate output. "
        "Write an English instruction that can take the given text as an appropriate answer.\n\n"
        "### Text:\n{instruction}\n\n### English Instruction:"
    ),
}

def read_jsonl(path:str):
    with open(path, "r", encoding="utf-8") as f:
        samples = [json.loads(l.strip()) for l in f.readlines()]
    return samples

def single_prompt(model, tokenizer, prompt="Hello, I'm am conscious and", max_new_tokens:int=128, do_sample:bool=True, num_beams:int=1, top_k:int=50, top_p:float=0.95, no_repeat_ngram_size=6, temperature:float=0.7, cuda=None, verbose=False):
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    if cuda:
        model = model.to(cuda)
        input_ids = input_ids.to(cuda)
    with torch.inference_mode():
        generated_ids = model.generate(input_ids=input_ids, max_new_tokens=max_new_tokens, do_sample=do_sample, num_beams=num_beams, top_k=top_k, top_p=top_p, temperature=temperature, no_repeat_ngram_size=no_repeat_ngram_size)
    results = tokenizer.batch_decode(generated_ids, skip_special_tokens=True, spaces_between_special_tokens=False)[0]
    inputs = tokenizer.batch_decode(input_ids, skip_special_tokens=True, spaces_between_special_tokens=False)[0]
    if verbose:
        print(results)
    return results if model.config.is_encoder_decoder else results[len(inputs):]

def infer_xIns(
    model, 
    tokenizer, 
    prompt, 
    is_xIns=False,
    is_aug=False,
    output_lang="English", 
    cuda=None
):
    # gen_dict = {
    #     "max_new_tokens": 128,
    #     "do_sample": False,
    #     "num_beams": 1,
    # }
    gen_dict = {
        "max_new_tokens": 2048,
        "do_sample": True,
        "top_p": 0.9,
        "temperature": 0.7,
    }
    in_format = "xres_prompt_no_input" if not is_xIns else "xins_prompt_no_input"
    if is_aug:
        in_format = "xres_aug_prompt_no_input"
    in_prompt = PROMPT_DICT[in_format].format_map({"instruction": prompt, "output_lang": output_lang})
    return single_prompt(model=model, tokenizer=tokenizer, prompt=in_prompt, cuda=cuda, **gen_dict)    

def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, required=True)
    parser.add_argument("--prompt", type=str, required=True)
    parser.add_argument("--output_lang", type=str, default="English")
    parser.add_argument("--is_xIns", action="store_true")
    parser.add_argument("--is_aug", action="store_true")
    parser.add_argument("--cuda", type=str, default=None)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    model = AutoModelForCausalLM.from_pretrained(args.model_path)
    tokenizer = AutoTokenizer.from_pretrained(args.model_path)
    response = infer_xIns(model, tokenizer, args.prompt, args.is_xIns, args.is_aug, args.output_lang, args.cuda)


    # xRes_path = "PATH2X-Instruction-7b-10langs"
    # xRes_model = AutoModelForCausalLM.from_pretrained(xRes_path, torch_dtype=torch.bfloat16)
    # tok = AutoTokenizer.from_pretrained(xRes_path)

    # # English prompt
    # prompt = "Give some tips on how to design a trip to New York."
    # # Urdu prompt (0-shot)
    # # prompt = "نیویارک کے سفر کو ڈیزائن کرنے کے بارے میں کچھ تجاویز دیں۔"
    
    # # The languages of "X-Instruction-7b-10langs" are Bengali, Finnish, Hindi, Indonesian, Swahili, Tamil, Thai, Turkish, Urdu, and Vietnamese
    # output_lang = "Urdu"

    # # Response in output_lang:
    # response = infer_xIns(xRes_model, tok, prompt=prompt, is_xIns=False, is_aug=True, output_lang=output_lang, cuda="cuda:0")
