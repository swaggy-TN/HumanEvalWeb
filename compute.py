import json
import sys
Q1= {
    'Q1_Ans1':0,
    'Q1_Ans2':0,
    'Q1_Tie':0}
Q2 = {
    'Q2_Ans1':0,
    'Q2_Ans2':0,
    'Q2_both':0,
    'Q2_neither':0,
}
Q3 = {
    'Q3_Ans1':0,
    'Q3_Ans2':0,
    'Q3_both':0,
    'Q3_neither':0,
}

if __name__ == '__main__':
    eval_file = sys.argv[1]
    with open(eval_file, 'r+', encoding='utf-8') as f:
        for item in f:
            item = json.loads(item)
            a,b,c = item['answer']
            Q1[a] += 1
            Q2[b] += 1
            Q3[c] += 1
    print(Q1)
    print(Q2)
    print(Q3)