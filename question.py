# question.py
import random


def calculate_difficulty(num1, num2, operator):
    """Calculate the difficulty of a question and return a damage value (1-3)"""
    # Base difficulty factors by operator
    operator_difficulty = {
        "+": 1,
        "-": 1.2,
        "*": 2,
        "/": 3
    }

    size_difficulty = 1

    # Adjust difficulty based on number size
    if operator in ["+", "-"]:
        # For addition/subtraction, larger numbers are harder
        max_num = max(num1, num2)
        if max_num > 20:
            size_difficulty = 1.5
        if max_num > 40:
            size_difficulty = 2
    elif operator == "*":
        # For multiplication, both numbers matter
        if num1 > 10 or num2 > 10:
            size_difficulty = 1.5
        if num1 > 20 or num2 > 20:
            size_difficulty = 2.5
    elif operator == "/":
        # For division, larger divisors are harder
        if num2 > 5:
            size_difficulty = 1.5

    # Calculate final difficulty score
    difficulty_score = operator_difficulty[operator] * size_difficulty

    # Map to damage (1-3 scale)
    damage = 1  # Base damage
    if difficulty_score > 2.5:
        damage = 3
    elif difficulty_score > 1.5:
        damage = 2

    return damage


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

    # Calculate question difficulty and corresponding damage
    damage = calculate_difficulty(num1, num2, operator)

    question = f"{num1} {operator} {num2} = ?"
    return question, answer, damage