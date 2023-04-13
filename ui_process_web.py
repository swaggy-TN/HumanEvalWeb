def get_initial_data(json_data):
    initial_data = {
        "question": json_data[0]["question"],
        "ans1": json_data[0]["ans1"],
        "ans2": json_data[0]["ans2"],
    }
    return initial_data
