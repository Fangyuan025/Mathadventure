# game.py
import pygame
pygame.init()

import time
from player import Player
from monster import Monster
from question import generate_question
from utils import draw_text, generate_sound
from constants import *


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Math Adventure Game")

# Sound effects
correct_sound = generate_sound(1000, 0.1)
incorrect_sound = generate_sound(200, 0.1)
timeout_sound = generate_sound(300, 0.5)


def main():
    player = Player()
    game_level = 1
    monsters_defeated = 0
    questions_answered = 0
    previous_questions = []
    question_start_time = 0
    TIME_LIMIT = 10  # seconds per question

    def create_monster():
        monsters_needed = 3 + game_level // 2  # Scale monsters per level
        if questions_answered >= monsters_needed:
            return None  # Trigger level up

        if game_level % 3 == 0:  # Boss every 3 levels
            return Monster(hp=5 + game_level * 2, level=game_level, x=600, y=500, is_boss=True)
        return Monster(hp=2 + game_level, level=game_level, x=600, y=500)

    def new_question():
        nonlocal question_start_time
        while True:
            question, answer = generate_question(game_level)
            if question not in previous_questions[-3:]:  # Prevent recent duplicates
                previous_questions.append(question)
                if len(previous_questions) > 5:
                    previous_questions.pop(0)
                question_start_time = time.time()
                return question, answer

    monster = create_monster()
    question, correct_answer = new_question()
    input_active = False
    user_input = ""
    running = True

    while running:
        screen.fill(WHITE)
        current_time = time.time()
        elapsed_time = current_time - question_start_time

        # Handle timeout
        if input_active and elapsed_time > TIME_LIMIT:
            timeout_sound.play()
            player.hp -= 1
            input_active = False
            if player.hp <= 0:
                running = False
            question, correct_answer = new_question()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.move("left")
                elif event.key == pygame.K_RIGHT:
                    player.move("right")
                elif event.key == pygame.K_SPACE and not input_active:
                    input_active = True
                    user_input = ""
                    question_start_time = time.time()
                elif input_active:
                    if event.key == pygame.K_RETURN:
                        if user_input == str(correct_answer):
                            correct_sound.play()
                            monster.hp -= 1
                            player.score += 10 * game_level
                            questions_answered += 1

                            if monster.hp <= 0:
                                monsters_defeated += 1
                                if monster.is_boss:
                                    player.score += 100
                                monster = create_monster()
                                if not monster:  # Level up
                                    game_level += 1
                                    questions_answered = 0
                                    monster = create_monster()
                        else:
                            incorrect_sound.play()
                            player.hp -= 1
                            if player.hp <= 0:
                                running = False

                        question, correct_answer = new_question()
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        user_input = user_input[:-1]
                    else:
                        user_input += event.unicode

        # Drawing
        player.draw(screen)
        if monster:
            monster.draw(screen)

        # UI Elements
        draw_text(screen, f"Level: {game_level}", BLACK, 10, 10)
        draw_text(screen, f"Score: {player.score}", BLACK, 10, 50)
        draw_text(screen, f"HP: {player.hp}", BLACK, 10, 90)

        if input_active:
            time_remaining = max(0, TIME_LIMIT - elapsed_time)
            draw_text(screen, f"Time: {time_remaining:.1f}s", RED, 600, 50)
            draw_text(screen, question, BLACK, 300, 200)
            draw_text(screen, f"Your answer: {user_input}", BLACK, 300, 300)
        else:
            draw_text(screen, "Press SPACE to attack", BLACK, 300, 200)

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()