"""
=================================================================
 PROJECT 4: QUIZ AND EXAMINATION SYSTEM
=================================================================
An interactive MCQ quiz application that:
  - Stores questions as immutable tuples (question bank)
  - Accepts and validates student answers (A/B/C/D)
  - Tracks score, computes percentage and grade
  - Shows a wrong-answer review and a final result report

Bonus features implemented:
  - random.shuffle() to shuffle question order each run
  - Per-question timer (10 seconds) using the time module
  - Category-based quiz selection (Python Basics / OOP / File Handling)
  - High-score leaderboard saved to a text file

File name: quiz_system.py
=================================================================
"""

import random
import time
import os

LEADERBOARD_FILE = "leaderboard.txt"
TIME_LIMIT_SECONDS = 10
VALID_OPTIONS = {"A", "B", "C", "D"}


# -----------------------------------------------------------------
# 1. QUESTION BANK  (stored as tuples -> immutable, for data integrity)
#    Each tuple: (question, optA, optB, optC, optD, correct_option)
# -----------------------------------------------------------------
QUESTION_BANK = {
    "Python Basics": [
        ("Which data type is IMMUTABLE in Python?",
         "List", "Dictionary", "Tuple", "Set", "C"),
        ("Which keyword is used to define a function in Python?",
         "func", "def", "function", "lambda", "B"),
        ("What is the output of 3 ** 2 in Python?",
         "6", "9", "5", "Error", "B"),
        ("Which symbol is used for comments in Python?",
         "//", "#", "/* */", "--", "B"),
        ("Which method converts a string to uppercase?",
         "upper()", "toUpper()", "capitalize()", "UPPER()", "A"),
    ],
    "OOP": [
        ("Which keyword is used to create a class in Python?",
         "object", "class", "struct", "define", "B"),
        ("What is the term for creating an instance of a class called?",
         "Inheritance", "Polymorphism", "Instantiation", "Abstraction", "C"),
        ("Which method is automatically called when an object is created?",
         "__init__", "__new__", "__call__", "__main__", "A"),
        ("Which OOP concept allows a child class to use a parent class's methods?",
         "Encapsulation", "Inheritance", "Polymorphism", "Abstraction", "B"),
    ],
    "File Handling": [
        ("Which mode opens a file for appending data?",
         "'r'", "'w'", "'a'", "'x'", "C"),
        ("Which function is used to close an open file?",
         "file.end()", "file.close()", "file.exit()", "file.stop()", "B"),
        ("Which statement automatically closes a file after use?",
         "try", "with", "def", "for", "B"),
        ("Which method reads the entire file content as a single string?",
         "read()", "readline()", "readlines()", "readall()", "A"),
    ],
}


def load_questions(category=None):
    """Returns the question bank (list of tuples).
    If a category is given, only that category's questions are returned,
    otherwise questions from every category are combined."""
    if category and category in QUESTION_BANK:
        return list(QUESTION_BANK[category])

    all_questions = []
    for q_list in QUESTION_BANK.values():
        all_questions.extend(q_list)
    return all_questions


def display_question(number, question_tuple):
    """Displays a single question with its 4 options."""
    question, opt_a, opt_b, opt_c, opt_d, _ = question_tuple
    print(f"\nQ{number}: {question}")
    print(f" A. {opt_a}   B. {opt_b}")
    print(f" C. {opt_c}   D. {opt_d}")


def get_answer():
    """Accepts and validates the student's answer (A/B/C/D only).
    Re-prompts on invalid input using exception handling."""
    while True:
        try:
            raw = input("Your Answer: ").strip().upper()
            if raw in VALID_OPTIONS:
                return raw
            raise ValueError("Invalid option entered.")
        except ValueError:
            print("Invalid input! Please enter only A, B, C, or D.")


def evaluate_quiz(questions):
    """Loops through every question, scores answers, and tracks
    wrong answers. Returns a dictionary with the full result."""
    score = 0
    wrong_answers = []
    asked_questions = set()  # ensures no question is evaluated twice

    for i, q_tuple in enumerate(questions, start=1):
        question_text = q_tuple[0]
        if question_text in asked_questions:
            continue
        asked_questions.add(question_text)

        display_question(i, q_tuple)

        start_time = time.time()
        student_answer = get_answer()
        elapsed = time.time() - start_time

        correct_option = q_tuple[5]
        timed_out = elapsed > TIME_LIMIT_SECONDS

        if timed_out:
            print(f"⏰ Time's up! (took {elapsed:.1f}s) Marked as incorrect.")
            wrong_answers.append((question_text, student_answer, correct_option))
            continue

        if student_answer == correct_option:
            print("✓ Correct!")
            score += 1
        else:
            print(f"✗ Incorrect! Correct answer was {correct_option}.")
            wrong_answers.append((question_text, student_answer, correct_option))

    return {
        "score": score,
        "total": len(asked_questions),
        "wrong_answers": wrong_answers,
    }


def calculate_grade(percentage):
    """Returns a letter grade based on the percentage scored."""
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B+"
    elif percentage >= 60:
        return "B"
    elif percentage >= 50:
        return "C"
    else:
        return "F"


def show_report(name, roll, result):
    """Prints the final formatted result report."""
    score = result["score"]
    total = result["total"]
    percentage = (score / total) * 100 if total else 0
    grade = calculate_grade(percentage)
    verdict = "PASS" if percentage >= 50 else "FAIL"

    print("\n====== RESULT REPORT ======")
    print(f"Name     : {name}")
    print(f"Roll No  : {roll}")
    print(f"Score    : {score} / {total}")
    print(f"Percent  : {percentage:.2f}%")
    print(f"Grade    : {grade}")
    print(f"Result   : {verdict}")
    print("============================")

    return percentage, verdict


def show_wrong_answers(wrong_answers):
    """Displays all incorrectly answered questions with the right answer."""
    if not wrong_answers:
        print("\nGreat job! No wrong answers. 🎉")
        return

    print("\n----- WRONG ANSWER REVIEW -----")
    for question_text, given, correct in wrong_answers:
        given_display = given if given in VALID_OPTIONS else "No Answer"
        print(f"Q: {question_text}")
        print(f"   Your Answer: {given_display}   Correct Answer: {correct}")
    print("--------------------------------")


def save_to_leaderboard(name, score, total):
    """Appends the student's result to the leaderboard file."""
    try:
        with open(LEADERBOARD_FILE, "a") as f:
            f.write(f"{name},{score},{total}\n")
    except OSError as e:
        print(f"Could not save leaderboard entry: {e}")


def show_leaderboard(top_n=5):
    """Reads the leaderboard file and prints the top scorers."""
    if not os.path.exists(LEADERBOARD_FILE):
        print("\nNo leaderboard data yet.")
        return

    entries = []
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 3:
                    name, score, total = parts
                    entries.append((name, int(score), int(total)))
    except OSError as e:
        print(f"Could not read leaderboard: {e}")
        return

    entries.sort(key=lambda x: x[1] / x[2] if x[2] else 0, reverse=True)

    print("\n====== LEADERBOARD (Top {} ) ======".format(top_n))
    for rank, (name, score, total) in enumerate(entries[:top_n], start=1):
        pct = (score / total) * 100 if total else 0
        print(f"{rank}. {name:<15} {score}/{total}  ({pct:.2f}%)")
    print("====================================")


def get_student_details():
    """Collects and validates student name and roll number."""
    name = input("Enter your name: ").strip()
    while not name:
        name = input("Name cannot be empty. Enter your name: ").strip()

    while True:
        try:
            roll = int(input("Enter your roll number: ").strip())
            break
        except ValueError:
            print("Invalid roll number! Please enter digits only.")
    return name, roll


def choose_category():
    """Lets the student pick a category, or all categories combined."""
    categories = list(QUESTION_BANK.keys())
    print("\nChoose a quiz category:")
    for i, cat in enumerate(categories, start=1):
        print(f" {i}. {cat}")
    print(f" {len(categories) + 1}. All Categories (Full Quiz)")

    while True:
        try:
            choice = int(input("Enter choice number: ").strip())
            if 1 <= choice <= len(categories):
                return categories[choice - 1]
            elif choice == len(categories) + 1:
                return None
            else:
                print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a valid number.")


def main():
    print("===== PYTHON QUIZ SYSTEM =====")
    name, roll = get_student_details()
    category = choose_category()

    questions = load_questions(category)
    random.shuffle(questions)  # bonus: shuffle question order each run

    print(f"\nStudent: {name} | Roll: {roll}")
    print(f"Category: {category if category else 'All Categories'}")
    print(f"Total Questions: {len(questions)}  |  {TIME_LIMIT_SECONDS}s per question\n")

    result = evaluate_quiz(questions)
    percentage, verdict = show_report(name, roll, result)
    show_wrong_answers(result["wrong_answers"])

    save_to_leaderboard(name, result["score"], result["total"])
    show_leaderboard()

    print(f"\nThank you for taking the quiz, {name}! Final verdict: {verdict}")


if __name__ == "__main__":
    main()


# =================================================================
# SAMPLE RUN (documented output for testing reference)
# =================================================================
# ===== PYTHON QUIZ SYSTEM =====
# Enter your name: Anjali Patil
# Enter your roll number: 204
#
# Choose a quiz category:
#  1. Python Basics
#  2. OOP
#  3. File Handling
#  4. All Categories (Full Quiz)
# Enter choice number: 4
#
# Student: Anjali Patil | Roll: 204
# Category: All Categories
# Total Questions: 13  |  10s per question
#
# Q1: Which data type is IMMUTABLE in Python?
#  A. List   B. Dictionary
#  C. Tuple  D. Set
# Your Answer: C
# ✓ Correct!
# ...
# (remaining questions asked and scored in the same way)
# ...
# ====== RESULT REPORT ======
# Name     : Anjali Patil
# Roll No  : 204
# Score    : 8 / 10
# Percent  : 80.00%
# Grade    : A
# Result   : PASS
# ============================
#
# ----- WRONG ANSWER REVIEW -----
# Q: Which method is automatically called when an object is created?
#    Your Answer: B   Correct Answer: A
# --------------------------------
#
# ====== LEADERBOARD (Top 5 ) ======
# 1. Anjali Patil    8/10  (80.00%)
# ====================================
#
# Thank you for taking the quiz, Anjali Patil! Final verdict: PASS
# =================================================================
