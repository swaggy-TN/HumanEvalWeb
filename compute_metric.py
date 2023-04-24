import argparse
import json
import os

import openai
import tqdm
import ray
import time
from collections import defaultdict
from tqdm import tqdm
import numpy as np

MAX_SCORE_ORDER=10

def read_jsonl(path: str, key: str=None):
    data = []
    with open(os.path.expanduser(path)) as f:
        for line in f:
            if not line:
                continue
            data.append(json.loads(line))
    if key is not None:
        data.sort(key=lambda x: x[key])
        data = {item[key]: item for item in data}
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-r', '--review')
    parser.add_argument('-l', '--language-list', nargs='+', default=['en', 'zh'])
    parser.add_argument('--order', action='store_true')
    args = parser.parse_args()

    all_metrics = {}
    for target_lang in args.language_list:
        lang_path = os.path.join(args.review, target_lang)

        review_files = os.listdir(lang_path)
        review_files = list(filter(lambda x: x.endswith('.jsonl'), review_files))
        
        res_list = []
        for review_file in review_files:
            
            review = read_jsonl(os.path.join(lang_path, review_file), key='question_id')
            n_question = len(review)

            id1 = list(review.keys())[0]
            if 'metadata' in review[id1]:
                model_ids = review[id1]['metadata']['model_ids']
            else:
                model_ids = review_file.split('.jsonl')[0][2:].split('-switch-side')[0].split('_vs_')

            order_count = defaultdict(lambda: 0)
            score_count = defaultdict(lambda: 0)
            n_skip = 0
            for qid in review.keys():
                category = review[qid]['category']

                if args.order:
                    if -1 in review[qid]['order']:
                        n_skip += 1
                        continue

                    model_orders = review[qid]['order']
                    for model_id, model_order in zip(model_ids, model_orders):
                        order_count[model_id] += model_order
                        score_count[model_id] += MAX_SCORE_ORDER / model_order
                else:
                    if -1 in review[qid]['score']:
                        n_skip += 1
                        continue

                    model_scores = review[qid]['score']

                    for model_id, model_score in zip(model_ids, model_scores):
                        score_count[model_id] += model_score
            

            res = {}
            for model_id in model_ids:
                res[model_id] = {}
                res[model_id]['score'] = score_count[model_id] / (n_question - n_skip)
                if args.order:
                    res[model_id].update({
                        'order': order_count[model_id] / (n_question - n_skip),
                    })
            res_list.append(res)

        model_id1, model_id2 = model_ids[0], model_ids[1]
        lang_metric = {
            model_id1: {
                'score': np.mean([res[model_id1]['score'] for res in res_list]),
                'ranking score': np.mean([res[model_id1]['order'] for res in res_list]),
            },
            model_id2: {
                'score': np.mean([res[model_id2]['score'] for res in res_list]),
                'ranking score': np.mean([res[model_id2]['order'] for res in res_list]),
            },
        }

        if lang_metric[model_id1]['ranking score'] < lang_metric[model_id2]['ranking score']:
            lang_metric['final_ranking'] = f'{model_id1} > {model_id2}'
        elif lang_metric[model_id1]['ranking score'] > lang_metric[model_id2]['ranking score']:
            lang_metric['final_ranking'] = f'{model_id1} < {model_id2}'
        else:
            lang_metric['final_ranking'] = f'{model_id1} = {model_id2}'

        lang_metric['all_ranking'] = {
            f'{model_id1} > {model_id2}': sum([res[model_id1]['order'] < res[model_id2]['order'] for res in res_list]),
            f'{model_id1} = {model_id2}': sum([res[model_id1]['order'] == res[model_id2]['order'] for res in res_list]),
            f'{model_id1} < {model_id2}': sum([res[model_id1]['order'] > res[model_id2]['order'] for res in res_list]),
        }
                        
        
        output_file = os.path.join(lang_path, 'metric.json')
        with open(output_file, 'w') as f:
            f.write(json.dumps(lang_metric, indent=4) + '\n')

        print(f'Output to {output_file}')
        print()

        all_metrics[target_lang] = lang_metric


    output_file = os.path.join(args.review, 'all_metrics.json')
    with open(output_file, 'w') as f:
        f.write(json.dumps(all_metrics, indent=4) + '\n')

    print(f'Output to {output_file}')
    print()

