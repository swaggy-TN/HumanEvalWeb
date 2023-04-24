export OPENAI_API_KEY="your openai api key"

langs=(ar de ja)

for lang in ${langs[*]};do
    echo "Start Evaluation"
    python generate_answer-api.py --question questions/question_$lang\_100.jsonl --output $lang-outputs/answer_gpt35.jsonl
    echo "Finished"
done