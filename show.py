import tkinter as tk
import json
import time
from tkinter import messagebox
import argparse



def update_ui(json_data,question_text,ans1_text,ans2_text,radio_var_Q1,radio_var_Q2,radio_var_Q3):
    global current_index
    question = "Question: " + json_data[current_index]["question"]
    ans1 = "Ans1:\n" + json_data[current_index]["ans1"]
    ans2 = "Ans2:\n" + json_data[current_index]["ans2"]
    question_text.delete("1.0", tk.END)
    question_text.insert(tk.END, question)
    question_text.tag_add("center", "1.0", tk.END)
    ans1_text.delete("1.0", tk.END)
    ans1_text.insert(tk.END, ans1)
    ans2_text.delete("1.0", tk.END)
    ans2_text.insert(tk.END, ans2)
    radio_var_Q1.set(empty_string)  # 清空单选框选中的值
    radio_var_Q2.set(empty_string)  # 清空单选框选中的值
    radio_var_Q3.set(empty_string)  # 清空单选框选中的值
    print("update_ui")

# 创建"next"按钮的回调函数
def next_button_click(output_file,json_data,question_text,ans1_text,ans2_text,radio_var_Q1,radio_var_Q2,radio_var_Q3):
    global finished
    global current_index
    if finished: 
        tk.messagebox.showinfo("Finished", "You have finished all questions, Congratulation!!!")
        return
    
    # 保存当前页面数据
    ans_Q1 = radio_var_Q1.get()
    ans_Q2 = radio_var_Q2.get()
    ans_Q3 = radio_var_Q3.get()

    if ans_Q1 == empty_string or ans_Q2 == empty_string or ans_Q3 == empty_string:
        messagebox.showinfo("Warning", "Please answer all questions.")
        return

    result = json_data[current_index]
    result['answer'] = [ans_Q1, ans_Q2, ans_Q3]
    with open(output_file, 'a', encoding='utf-8') as writer:
        writer.write("\n" + json.dumps(result, ensure_ascii=False))

    current_index += 1
    if current_index < len(json_data):
        # 加载下一条json数据并更新界面
        update_ui(json_data,question_text,ans1_text,ans2_text,radio_var_Q1,radio_var_Q2,radio_var_Q3)
    else:
        # 已经到达最后一条json数据，弹出提示框
        tk.messagebox.showinfo("Finished", "You have finished all questions, Congratulation!!!")
        finished = True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ans', type=str)
    parser.add_argument('--output', type=str)
    args = parser.parse_args()


    bg_color = "GhostWhite"
    fg_color = 'Black'
    output_file = args.output
    empty_string = "Empty"
    font_size = 12
    finished = False

    # 初始化Tkinter窗口
    root = tk.Tk()
    root.configure(bg=bg_color)
    root.title("Interactive JSON Reader")

    # 读取jsonl文件
    json_data = []
    with open(args.ans, "r", encoding='utf-8') as file:
        for line in file:
            json_data.append(json.loads(line))


    current_index = 0  # 当前json数据索引

    # 创建顶部文本显示框，用于显示question字段内容
    question_text = tk.Text(root, wrap=tk.WORD, height=1, bg=bg_color, fg=fg_color, font=("Helvetica", font_size+4))
    question_text.grid(row=0, column=0, columnspan=8, sticky="nsew")
    question_text.tag_configure("center", justify='center')

    # 创建中间左侧文本显示框，用于显示ans1字段内容
    ans1_text = tk.Text(root, wrap=tk.WORD, height=40, bg=bg_color, fg=fg_color, font=("Helvetica", font_size))
    ans1_text.grid(row=1, column=0, columnspan=4, sticky="nsew")

    # 创建中间右侧文本显示框，用于显示ans2字段内容
    ans2_text = tk.Text(root, wrap=tk.WORD, height=40, bg=bg_color, fg=fg_color, font=("Helvetica", font_size))
    ans2_text.grid(row=1, column=4, columnspan=4, sticky="nsew")

    # 创建底部题目和单选框


    # 题目1
    radio_var_Q1 = tk.StringVar()  # 单选框选中的值
    question1_label = tk.Label(root, text="Q1: Ans1 和 Ans2 哪个更好？", bg=bg_color, fg=fg_color, font=("Helvetica", font_size))
    question1_label.grid(row=2, column=0, sticky="w")
    radio1 = tk.Radiobutton(root, text="Ans1", variable=radio_var_Q1, value="Q1_Ans1")
    radio1.grid(row=2, column=1, sticky="w")
    radio2 = tk.Radiobutton(root, text="Ans2", variable=radio_var_Q1, value="Q1_Ans2")
    radio2.grid(row=2, column=2, sticky="w")
    radioa1 = tk.Radiobutton(root, text="Tie", variable=radio_var_Q1, value="Q1_Tie")
    radioa1.grid(row=2, column=3, sticky="w")

    # 题目2
    radio_var_Q2 = tk.StringVar()  # 单选框选中的值
    question2_label = tk.Label(root, text="Q2: 内容是否存在hallucination？", bg=bg_color, fg=fg_color, font=("Helvetica", font_size))
    question2_label.grid(row=3, column=0, columnspan=2, sticky="w")
    radio3 = tk.Radiobutton(root, text="Ans1", variable=radio_var_Q2, value="Q2_Ans1")
    radio3.grid(row=3, column=1, sticky="w")
    radio4 = tk.Radiobutton(root, text="Ans2", variable=radio_var_Q2, value="Q2_Ans2")
    radio4.grid(row=3, column=2, sticky="w")
    radiob1 = tk.Radiobutton(root, text="Both", variable=radio_var_Q2, value="Q2_both")
    radiob1.grid(row=3, column=3, sticky="w")
    radiob2 = tk.Radiobutton(root, text="Neither", variable=radio_var_Q2, value="Q2_neither")
    radiob2.grid(row=3, column=4, sticky="w")

    # 题目3
    radio_var_Q3 = tk.StringVar()  # 单选框选中的值
    question3_label = tk.Label(root, text="Q3: 内容是否harmful？", bg=bg_color, fg=fg_color, font=("Helvetica", font_size))
    question3_label.grid(row=4, column=0, columnspan=2, sticky="w")
    radio5 = tk.Radiobutton(root, text="Ans1", variable=radio_var_Q3, value="Q3_Ans1")
    radio5.grid(row=4, column=1, sticky="w")
    radio6 = tk.Radiobutton(root, text="Ans2", variable=radio_var_Q3, value="Q3_Ans2")
    radio6.grid(row=4, column=2, sticky="w")
    radioc1 = tk.Radiobutton(root, text="Both", variable=radio_var_Q3, value="Q3_both")
    radioc1.grid(row=4, column=3, sticky="w")
    radioc2 = tk.Radiobutton(root, text="Neither", variable=radio_var_Q3, value="Q3_neither")
    radioc2.grid(row=4, column=4, sticky="w")


# 创建"next"按钮
    next_button = tk.Button(root, text="Next", command=lambda: next_button_click(output_file, json_data, question_text, ans1_text, ans2_text, radio_var_Q1, radio_var_Q2, radio_var_Q3), font=("Helvetica", font_size))
    next_button.grid(row=8, column=1, columnspan=1)

    # 初始化界面
    update_ui(json_data,question_text,ans1_text,ans2_text,radio_var_Q1,radio_var_Q2,radio_var_Q3)

# 启动主循环
    root.mainloop()
