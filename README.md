# GPT-4 Eval

Given a pair of candidate answers, here is the pipeline to rate these answers by calling openai APIs:

## Step 1 
First make sure the question file is in the `questions/` directory, the answer file is in the `answers/` directory and the number of candidate answers strictly corresponding to the number of questions. 

## Step 2
See the `evaluate.sh`
```bash
#GPT-4
langs=(ja es pt de it)
rule=prompt.jsonl
for lang in ${langs[*]};do
        question=questions/question_$lang\_100.jsonl
        answer1=$lang-outputs/answer_phoenix-inst-chat-7b.jsonl
        answer2=$lang-outputs/answer_gpt35.jsonl  
        output=$lang\_reviews/phoenix-inst-chat-7b_vs_gpt35.jsonl
        max_tokens=1024
        options="\
                --question $question \
                --answer-list $answer1 $answer2 \
                --rule $rule \
                --output $output \
                --max-tokens $max_tokens \
                "

        export SCRIPT_PATH=eval_gpt_review.py

        echo "Start Evaluation"
        python3 $SCRIPT_PATH $options
        echo "Finished"
done

```

modify the environment variables:`question`,`answer1`, `answer2` and `output`. If the `lang` vairable is no longer needed you can directly delete it in the shell scripts and test the candidate answer pairs one by one.

## Step 3

Once you received the reveiws, you can use this CLI:
```bash
python compute_score.py --review /path/to/review.jsonl
```
I added a randomly switch-side function to alleviate the position bias of the GPT4 evaluation. So if the naming of your review file has a suffix of `-switch-side.jsonl`, you will have to add `--switch` in the aforementioned CLI.

NB: if the number of questions isn't equal 100, you will have to modify the code in the `compute_score.py` at line 29 and line 30:
```python
    model1score/=100
    model2score/=100
```


It's the same case if you want to obtain a coarse-grained comparision (order) of the candidate pairs. 
The difference is that you have to use `evaluate_order.sh`.

