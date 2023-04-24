import argparse
import json
import os
import backoff
import openai
import tqdm
import ray
import time
import random
import re
import numpy as np
from retry import retry

@ray.remote(num_cpus=4)
@retry(tries=3)
@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
def get_eval(content: str, reviewer, temp=0.2):
    response = openai.ChatCompletion.create(
        model=reviewer,
        messages=[{
            'role': 'system',
            'content': 'You are a helpful and precise assistant for checking the quality of the answer.'
        }, {
            'role': 'user',
            'content': content,
        }],
        temperature=temp,  # TODO: figure out which temperature is best for evaluation
        # max_tokens=max_tokens,
    )
    return response['choices'][0]['message']['content']



def parse_score(review):
    try:
        score_pair = review.split('\n')[0]
        score_pair = score_pair.replace(',', ' ')
        sp = score_pair.split(' ')
        if len(sp) == 2:
            return [float(sp[0]), float(sp[1])]
        else:
            print('error', review)
            return [-1, -1]
    except Exception as e:
        print(e)
        print('error', review)
        return [-1, -1]


def parse_order_cot(review):
    review = re.sub(r'>=', '>', review)
    review = re.sub(r'>>', '>', review)
    try:
        ls = re.findall(r'(Assistant \d( [>=] Assistant \d)+)', review.strip())
        order_texts = [x[0] for x in ls]
        idxs = np.where(np.array([len(re.findall(r'Assistant', text)) == 2 for text in order_texts]))[0]
        if idxs.shape[0] != 0:
            order_text = order_texts[idxs[0]]

            ordered_assist = [int(x) for x in re.findall(r'\d', order_text)]
            ordered_comp = re.findall(r'[>=]', order_text)

            order = [0, 0]
            cur_order = 1
            num_eq = 0
            order[ordered_assist[0]-1] = cur_order
            for comp, assist in zip(ordered_comp, ordered_assist[1:]):
                if comp == '>':
                    cur_order += num_eq + 1
                    order[assist-1] = cur_order
                    num_eq = 0
                else:
                    order[assist-1] = cur_order
                    num_eq += 1
            return order
        elif re.search(r'Assistant 1 < Assistant 2', review):
            return [2, 1]
        elif re.search(r'(=)', review):
            return [1, 1]
        else:
            return [-1, -1]
        

    except Exception as e:
        # print(e)
        # print('error', review)
        return [-1, -1]
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ChatGPT-based QA evaluation.')
    parser.add_argument('-q', '--question')
    # parser.add_argument('-a', '--answer')
    parser.add_argument('-a', '--answer-list', nargs='+', default=[])
    parser.add_argument('-r', '--rule')
    parser.add_argument('-o', '--output')
    parser.add_argument('--order', action='store_true')
    parser.add_argument('--cot', action='store_true')
    parser.add_argument('--gpt4', action='store_true')
    parser.add_argument('--max-tokens', type=int, default=1024, help='maximum number of tokens produced in the output')
    args = parser.parse_args()

    if args.gpt4:
        reviewer = 'gpt-4'
    else:
        reviewer = 'gpt-3.5-turbo'

    ray.init()

    dice = random.random()
    f_q = open(os.path.expanduser(args.question))
    if dice >= 0.5:
        f_ans1 = open(os.path.expanduser(args.answer_list[0]))
        f_ans2 = open(os.path.expanduser(args.answer_list[1]))
    else:
        f_ans1 = open(os.path.expanduser(args.answer_list[1]))
        f_ans2 = open(os.path.expanduser(args.answer_list[0]))
        prefix = args.output.split('.')[0]
        args.output = prefix + '-switch-side.jsonl'

    rule_dict = json.load(open(os.path.expanduser(args.rule), 'r'))

    review_file = open(f'{args.output}', 'w')

    js_list = []
    handles = []
    idx = 0
    for ques_js, ans1_js, ans2_js in zip(f_q, f_ans1, f_ans2):

        ques_id = json.loads(ques_js)['question_id']
        ques = json.loads(ques_js)['text']
        ans1 = json.loads(ans1_js)['text']
        ans2 = json.loads(ans2_js)['text']

        category = json.loads(ques_js)['category']
        if category in rule_dict:
            rule = rule_dict[category]
        else:
            rule = rule_dict['default']
        prompt = rule['prompt']
        role = rule['role']
        content = (f'[Question]\n{ques}\n\n'
                   f'[{role} 1]\n{ans1}\n\n[End of {role} 1]\n\n'
                   f'[{role} 2]\n{ans2}\n\n[End of {role} 2]\n\n'
                   f'[System]\n{prompt}\n\n')
        js_list.append({
            'review_id': idx+1,
            'reviewer': reviewer,
            'question_id': ques_id,
            'question': ques,
            'answer1': ans1,
            'answer2': ans2,
            'category': category})
        idx += 1
        if args.order:
            handles.append(get_eval.remote(content, reviewer, temp=0))
        else:
            handles.append(get_eval.remote(content, reviewer, temp=0.2))
        # To avoid the rate limit set by OpenAI

    n_errors = 0
    reviews = ray.get(handles)
    for idx, review in enumerate(reviews):
        if not args.order:
            if args.cot:
                raise ValueError
            scores = parse_score(review)
            js_list[idx]['text'] = review
            js_list[idx]['score'] = scores
            if -1 in scores:
                n_errors += 1
        else:
            if not args.cot:
                raise ValueError
            orders = parse_order_cot(review)
            js_list[idx]['text'] = review
            js_list[idx]['order'] = orders
            if -1 in orders:
                n_errors += 1

        review_file.write(json.dumps(js_list[idx],ensure_ascii=False) + '\n')

    review_file.close()
    print(f'Output to {args.output}')
    print(f'There are {n_errors} reviews failing to decode.')
