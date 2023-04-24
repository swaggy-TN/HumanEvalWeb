import json
import argparse
import jsonlines
import sys


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
    parser.add_argument('-review', '--review')
    parser.add_argument('-switch', '--switch',action='store_true')
    args = parser.parse_args()


    reviews = reader(args.review)
    model1score, model2score = 0,0
    for review in reviews:
        scores = review['score']
        model1score += scores[0]
        model2score += scores[1]
    model1score/=100
    model2score/=100
    if not args.switch:
        print(f"phoenix score is {model1score} and model score is {model2score}")
    else:
        print(f"phoenix score is {model2score} and model score is {model1score}")

    # with jsonlines.open(args.output,'w') as g:
    #     for l in final:
    #         g.write(l)