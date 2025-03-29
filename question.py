# question.py
import random


def generate_question(level):
    if level == 1:
        num1 = random.randint(1, 20)
        num2 = random.randint(1, 20)
        operator = random.choice(["+", "-"])
    elif level <= 3:
        num1 = random.randint(1, 30)
        num2 = random.randint(1, 15)
        operator = random.choice(["+", "-", "*"])
    else:
        operator = random.choice(["+", "-", "*", "/"])
        if operator == "/":
            num2 = random.randint(1, 10)
            num1 = num2 * random.randint(1, 15)
        else:
            num1 = random.randint(1, 50)
            num2 = random.randint(1, 50)

    # Calculate answer
    if operator == "+":
        answer = num1 + num2
    elif operator == "-":
        answer = num1 - num2
    elif operator == "*":
        answer = num1 * num2
    else:  # Division (already ensured to be integer)
        answer = num1 // num2

    question = f"{num1} {operator} {num2} = ?"
    return question, answer
