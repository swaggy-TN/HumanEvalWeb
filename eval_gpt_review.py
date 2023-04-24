import argparse
import json
import os
import backoff
import openai
import tqdm
import ray
import time
import random

@ray.remote(num_cpus=4)
@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
def get_eval(content: str, max_tokens: int):
    response = openai.ChatCompletion.create(
        model='gpt-4',
        messages=[{
            'role': 'system',
            'content': 'You are a helpful and precise assistant for checking the quality of the answer.'
        }, {
            'role': 'user',
            'content': content,
        }],
        temperature=0.2,  # TODO: figure out which temperature is best for evaluation
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ChatGPT-based QA evaluation.')
    parser.add_argument('-q', '--question')
    # parser.add_argument('-a', '--answer')
    parser.add_argument('-a', '--answer-list', nargs='+', default=[])
    parser.add_argument('-r', '--rule')
    parser.add_argument('-o', '--output')
    parser.add_argument('--max-tokens', type=int, default=1024, help='maximum number of tokens produced in the output')
    args = parser.parse_args()

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
            'reviewer': 'gpt-4',
            'question_id': ques_id,
            'question': ques,
            'answer1': ans1,
            'answer2': ans2,
            'category': category})
        idx += 1
        handles.append(get_eval.remote(content, args.max_tokens))
        # To avoid the rate limit set by OpenAI


    reviews = ray.get(handles)
    for idx, review in enumerate(reviews):
        scores = parse_score(review)
        js_list[idx]['text'] = review
        js_list[idx]['score'] = scores
        review_file.write(json.dumps(js_list[idx],ensure_ascii=False) + '\n')
    review_file.close()
