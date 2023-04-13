from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_questions')
def get_questions():
    # Replace this with your actual JSON file
    questions = [
        {
            "question": "Which is better?",
            "ans1": "Answer 1",
            "ans2": "Answer 2"
        }
    ]
    return jsonify(questions)

@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    answers = request.get_json()
    print(answers)
    # Save the answers to a file or a database, as needed
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
