# game.py
import pygame
import time
import threading


from AttackEffect import AttackEffect
from player import Player
from monster import Monster
from question import generate_question
from utils import draw_text, generate_sound, draw_multiline_text
from constants import *
from local_llm import ask_local_llm
from FeedbackManager import feedback_manager

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Math Adventure Game")

# Sound effects
correct_sound = generate_sound(1000, 0.1)
incorrect_sound = generate_sound(200, 0.1)
timeout_sound = generate_sound(300, 0.5)

#setting
player_pos = [0,0]
target_pos = None
moving = False
selected_level = None

def draw_text(screen, text, color, x, y):
    font = pygame.font.Font(None, 36)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def main():
    player = Player()
    game_level = 1
    monsters_defeated = 0
    questions_answered = 0
    previous_questions = []
    question_start_time = 0
    waiting_for_attack_hit = False
    TIME_LIMIT = 10  # seconds per question
    attack_effect_img = pygame.image.load("assets/attack_effect.png")
    attack_effect_img = pygame.transform.scale(attack_effect_img, (60, 60))  # 可调整大小
    attack_effect = None
    waiting_for_next_question = False

    # Status: Map or Battle
    game_state = "map"
    selected_level = None
    map_bg_raw  = pygame.image.load("assets/map_background.png")
    map_bg = pygame.transform.scale(map_bg_raw, (WIDTH, HEIGHT))
    icon_raw = pygame.image.load("assets/player_icon.png")
    player_icon = pygame.transform.scale(icon_raw, (30, 30))
    player_pos = [50, 50]  # player location
    target_pos = None
    moving = False
    selected_level = None

    # Five level buttons
    battle_backgrounds = {
        1: pygame.transform.scale(pygame.image.load("assets/battle_bg_forest.jpg"), (WIDTH, HEIGHT)),
        2: pygame.transform.scale(pygame.image.load("assets/battle_bg_volcano.jpg"), (WIDTH, HEIGHT)),
        3: pygame.transform.scale(pygame.image.load("assets/battle_bg_volcano__desert.jpg"), (WIDTH, HEIGHT)),
        4: pygame.transform.scale(pygame.image.load("assets/battle_bg_volcano__snow.jpg"), (WIDTH, HEIGHT)),
        5: pygame.transform.scale(pygame.image.load("assets/battle_bg_forest.jpg"), (WIDTH, HEIGHT)),
    }
    levels = [
        {"rect": pygame.Rect(100, 100, 80, 80), "level": 1, "pos": (100, 100)},
        {"rect": pygame.Rect(150, 350, 80, 80), "level": 2, "pos": (150, 350)},
        {"rect": pygame.Rect(550, 360, 80, 80), "level": 3, "pos": (550, 360)},
        {"rect": pygame.Rect(550, 100, 80, 80), "level": 4, "pos": (550, 100)},
        {"rect": pygame.Rect(350, 200, 80, 80), "level": 5, "pos": (350, 200)},
    ]

    def return_to_map():
        nonlocal game_state, player_pos
        player_pos = get_right_of_level(selected_level)
        game_state = "map"

    def create_monster():
        monsters_needed = 3 + game_level // 2
        if questions_answered >= monsters_needed:
            return None
        if game_level % 3 == 0:
            return Monster(hp=5 + game_level * 2, level=game_level, x=600, y=500, is_boss=True)
        return Monster(hp=2 + game_level, level=game_level, x=600, y=500)


    def new_question():
        nonlocal question_start_time
        while True:
            question, answer = generate_question(game_level)
            if question not in previous_questions[-3:]:
                previous_questions.append(question)
                if len(previous_questions) > 5:
                    previous_questions.pop(0)
                question_start_time = time.time()
                return question, answer

    def get_right_of_level(level_num, offset=40):
        for lvl in levels:
            if lvl["level"] == level_num:
                x, y = lvl["pos"]
                return [x + offset, y]
        return [50, 50]  # fallback

    monster = None
    question = ""
    correct_answer = ""
    input_active = False
    user_input = ""
    running = True

    while running:
        screen.fill(WHITE)
        current_time = time.time()
        elapsed_time = current_time - question_start_time



        if game_state == "map" and moving and target_pos:
            dx = target_pos[0] - player_pos[0]
            dy = target_pos[1] - player_pos[1]
            distance = (dx ** 2 + dy ** 2) ** 0.5
            speed = 4  # set the player move speed

            if distance < speed:
                player_pos = list(target_pos)
                moving = False
                game_level = selected_level
                player.hp = player.max_hp
                player.score = 0
                questions_answered = 0
                monster = create_monster()
                question, correct_answer = new_question()
                input_active = False
                user_input = ""
                game_state = "battle"
            else:
                player_pos[0] += speed * dx / distance
                player_pos[1] += speed * dy / distance

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Battle mode button
            if game_state == "map":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for lvl in levels:
                        if lvl["rect"].collidepoint(event.pos):
                            target_pos = list(lvl["pos"])  # 目标位置
                            selected_level = lvl["level"]
                            moving = True
                            game_level = selected_level
                            player.hp = player.max_hp
                            player.score = 0
                            questions_answered = 0
                            monster = create_monster()
                            question, correct_answer = new_question()
                            input_active = False
                            user_input = ""


            # Battle mode button
            elif game_state == "battle":
                screen.blit(battle_backgrounds.get(game_level, map_bg), (0, 0))
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        player.move("left")
                    elif event.key == pygame.K_RIGHT:
                        player.move("right")
                    elif event.key == pygame.K_SPACE:
                        if feedback_manager.get():
                            feedback_manager.set("")
                            waiting_for_next_question = True  # 等待玩家再次按空格才进入新一题
                        elif waiting_for_next_question:
                            question, correct_answer = new_question()
                            waiting_for_next_question = False
                        elif not input_active:
                            input_active = True
                            user_input = ""
                            question_start_time = time.time()


                    elif input_active:
                        if event.key == pygame.K_RETURN:
                            if user_input == str(correct_answer):
                                correct_sound.play()

                                start_pos = [player.x + player.width // 2, player.y]
                                target_pos = [monster.x + monster.width // 2 - 30, monster.y + monster.height // 2 - 30]
                                attack_effect = AttackEffect(start_pos, target_pos, attack_effect_img)#effect location

                                waiting_for_attack_hit = True
                                input_active = False
                                user_input = ""
                                correct_sound.play()
                                # monster.hp -= 1
                                # player.score += 10 * game_level
                                # questions_answered += 1

                                if monster.hp <= 0:
                                    monsters_defeated += 1
                                    if monster.is_boss:
                                        player.score += 100

                                    monster = create_monster()
                                    if not monster:
                                        # back to map
                                        player_pos = get_right_of_level(selected_level)
                                        game_state = "map"
                                        continue
                            else:
                                incorrect_sound.play()
                                player.hp -= 1
                                feedback_manager.set("Generating feedback, please wait...")

                                def generate_feedback_async():
                                    questions = question
                                    correct_answers =correct_answer
                                    print(f"The question is  {question}")
                                    llm_answer = ask_local_llm(
                                        f"The student answered {user_input} to the math problem '{questions}', "
                                        f"but the correct answer is {correct_answers}. "
                                        f"Why is the student's answer wrong?"
                                    )
                                    feedback_manager.set(llm_answer)
                                threading.Thread(target=generate_feedback_async).start()

                                if player.hp <= 0:
                                    return_to_map()
                                    player_pos = get_right_of_level(selected_level)
                                    game_state = "map"
                                    continue
                            # question, correct_answer = new_question()
                            input_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            user_input = user_input[:-1]
                        else:
                            user_input += event.unicode

        # Game logic update
        if game_state == "battle":
            screen.blit(battle_backgrounds.get(game_level, map_bg), (0, 0))
            if input_active and elapsed_time > TIME_LIMIT:
                timeout_sound.play()
                player.hp -= 1
                input_active = False
                if player.hp <= 0:
                    return_to_map()
                    game_state = "map"
                    continue
                question, correct_answer = new_question()

        # Drawing interface
        if game_state == "map":
            screen.blit(map_bg, (0, 0))

            for lvl in levels:
                pygame.draw.rect(screen, BLUE, lvl["rect"])
                draw_text(screen, f"Level {lvl['level']}", WHITE, lvl["rect"].x + 10, lvl["rect"].y + 35)

            # set player icon
            screen.blit(player_icon, player_pos)
            draw_text(screen, "Select a Level", BLACK, 300, 30)

        elif game_state == "battle":
            player.draw(screen)

            if monster:
                monster.draw(screen)

            if feedback_manager.get():
                draw_multiline_text(screen, feedback_manager.get(), WIDTH // 2 - 290, 20, color=BLACK)


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

        if attack_effect:
            attack_effect.update()
            attack_effect.draw(screen)

            if not attack_effect.active:
                attack_effect = None

                if waiting_for_attack_hit and monster:
                    waiting_for_attack_hit = False

                    monster.hp -= 1
                    player.score += 10 * game_level
                    questions_answered += 1

                    if monster.hp <= 0:
                        monsters_defeated += 1
                        if monster.is_boss:
                            player.score += 100
                        monster = create_monster()
                        if not monster:
                            return_to_map()
                            continue
                    else:
                        question, correct_answer = new_question()

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
