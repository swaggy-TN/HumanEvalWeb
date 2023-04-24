#!/bin/bash
#GPT-3.5
# export OPENAI_API_KEY="your openai api key"
#GPT-4
export OPENAI_API_KEY="your openai api key"

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
