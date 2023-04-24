import json
import argparse
import jsonlines



def reader(file):
    question = []
    with open(file,'r') as f:
        for item in f:
            item = json.loads(item)
            question.append(item)
    f.close()
    return question

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-ans1', '--ans1')
    parser.add_argument('-ans2', '--ans2')
    parser.add_argument('-output', '--output_dir')
    args = parser.parse_args()

    ans1 = reader(args.ans1)
    ans2 = reader(args.ans2)
    question = reader('question_zh_100.jsonl')

    final = []
    for p,b,q in zip(ans1,ans2,question):
        neo_dict = {}
        neo_dict['question'] = q['text']
        neo_dict['ans1'] = p['text']
        neo_dict['ans2'] = b['text']
        neo_dict['eval_1'] = []
        neo_dict['eval_2'] = []
        final.append(neo_dict)

    with jsonlines.open(args.output,'w') as g:
        for l in final:
            g.write(l)