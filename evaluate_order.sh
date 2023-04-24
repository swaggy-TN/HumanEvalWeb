#!/bin/bash
#GPT-3.5
export OPENAI_API_KEY=""
#GPT-4
# export OPENAI_API_KEY=""

REVIEW_PATH=multilingual_review_order/chimera-inst-chat-13b_turbo

# lang_list=(ar de en es fr it ja ko pt)
lang_list=(de es fr it pt)
rule=prompt_order_cot.jsonl

model1=chimera-inst-chat-13b
model2=gpt35



echo "Start Evaluation"
for lang in ${lang_list[*]};do
        question=questions/question_$lang\_100.jsonl
        answer1=$lang-outputs/answer_$model1.jsonl
        answer2=$lang-outputs/answer_$model2.jsonl;

        mkdir $REVIEW_PATH/$lang
        output=$REVIEW_PATH/$lang/$i\_$model1\_vs_$model2.jsonl
        python3 eval_gpt_review_order.py \
                --question $question \
                --answer-list $answer1 $answer2 \
                --rule $rule \
                --order \
                --cot \
                --output $output
done
echo "Finished"

