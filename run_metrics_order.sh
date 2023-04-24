#!/bin/bash


PROJECT_PATH=/path/to/HumanEval
review=$PROJECT_PATH/multilingual_review_order/chimera-inst-chat-13b_turbo

# lang_list=(ar de en es fr it ja ko pt)
lang_list=(de es fr it pt)


echo "Start"
python $PROJECT_PATH/compute_metric.py \
        --review $review  \
        --language-list ${lang_list[*]} \
        --order
echo "Finish"





