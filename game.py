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
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Math Adventure Game")

# Sound effects
correct_sound = generate_sound(1000, 0.1)
incorrect_sound = generate_sound(200, 0.1)
timeout_sound = generate_sound(300, 0.5)

# setting
player_pos = [0, 0]
target_pos = None
moving = False
selected_level = None


def draw_text(screen, text, color, x, y):
    font = pygame.font.Font(None, 36)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))


def main():
    # Load and play map music at game start
    pygame.mixer.music.load("assets/map.mp3")
    pygame.mixer.music.set_volume(0.3)  # Adjust volume
    pygame.mixer.music.play(-1)  # Loop indefinitely

    monster_attack_phase = None  # 'to_player', 'returning', None
    monster_attack_start_time = 0
    monster_original_pos = (0, 0)
    monster_attack_target = (0, 0)
    monster_attack_damage_pending = False

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
    map_bg_raw = pygame.image.load("assets/map_background.png")
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
        # Switch to map music
        pygame.mixer.music.load("assets/map.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

    def create_monster():
        monsters_needed = 3 + game_level // 2
        if questions_answered >= monsters_needed:
            return None

        if game_level % 3 == 0:
            monster = Monster(hp=5 + game_level * 2, level=game_level, x=600, y=500, is_boss=True)
        else:
            monster = Monster(hp=2 + game_level, level=game_level, x=600, y=500)

        # Reset show-up animation
        monster.is_showing_up = True
        monster.show_up_timer = monster.show_up_duration
        monster.reset_hp_display()  # Reset HP display to match actual HP
        return monster

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
                # Switch to battle music
                pygame.mixer.music.load("assets/battle.mp3")
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
                player.is_showing_up = True
                player.show_up_timer = player.show_up_duration
                if monster:
                    monster.reset_hp_display()  # Ensure HP display is correct at battle start
            else:
                player_pos[0] += speed * dx / distance
                player_pos[1] += speed * dy / distance

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.USEREVENT + 1:
                # Death animation timer event - this fires when the animation is complete
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Cancel the timer

                # Check if this was the last monster in the level
                monsters_needed = 3 + game_level // 2
                if questions_answered >= monsters_needed:
                    # This was the last monster, return to map
                    return_to_map()
                else:
                    # Create a new monster and continue
                    monster = create_monster()
                    question, correct_answer = new_question()

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
                                attack_effect = AttackEffect(start_pos, target_pos,
                                                             attack_effect_img)  # effect location

                                waiting_for_attack_hit = True
                                input_active = False
                                user_input = ""
                                correct_sound.play()
                            else:
                                incorrect_sound.play()
                                # Start monster attack animation (delay HP loss)
                                monster_attack_phase = 'to_player'
                                monster_attack_start_time = time.time()
                                monster_original_pos = (monster.x, monster.y)
                                monster_attack_target = (
                                player.x + player.width // 2 - 50, player.y + player.height // 2)
                                monster_attack_damage_pending = True
                                input_active = False
                                user_input = ""

                                def generate_feedback_async():
                                    questions = question
                                    correct_answers = correct_answer
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
            if monster_attack_phase == 'to_player':
                attack_duration = 0.3  # seconds to reach player
                elapsed = time.time() - monster_attack_start_time
                if elapsed < attack_duration:
                    progress = elapsed / attack_duration
                    monster.x = monster_original_pos[0] + (
                                monster_attack_target[0] - monster_original_pos[0]) * progress
                    monster.y = monster_original_pos[1] + (
                                monster_attack_target[1] - monster_original_pos[1]) * progress
                else:
                    # Reached player: apply damage and start returning
                    monster_attack_phase = 'returning'
                    monster_attack_start_time = time.time()
                    if monster_attack_damage_pending:
                        player.hp -= 1
                        player.take_hit()
                        feedback_manager.set("Generating feedback, please wait...")

                        # Start feedback thread
                        def generate_feedback_async():
                            llm_answer = ask_local_llm(
                                f"The student answered {user_input} to '{question}', "
                                f"correct answer is {correct_answer}. Why wrong?"
                            )
                            feedback_manager.set(llm_answer)

                        threading.Thread(target=generate_feedback_async).start()
                        monster_attack_damage_pending = False

            elif monster_attack_phase == 'returning':
                return_duration = 0.3  # seconds to return
                elapsed = time.time() - monster_attack_start_time
                if elapsed < return_duration:
                    progress = elapsed / return_duration
                    monster.x = monster_attack_target[0] + (
                                monster_original_pos[0] - monster_attack_target[0]) * progress
                    monster.y = monster_attack_target[1] + (
                                monster_original_pos[1] - monster_attack_target[1]) * progress
                else:
                    # Reset monster position
                    monster.x, monster.y = monster_original_pos
                    monster_attack_phase = None
            if input_active and elapsed_time > TIME_LIMIT:
                timeout_sound.play()
                player.hp -= 1
                player.take_hit()  # Trigger player shake effect
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

                    # Use the new damage method instead of set_hp
                    monster.damage(1)  # Directly reduce HP and handle animations
                    monster.take_hit()  # Extra visual effects
                    player.score += 10 * game_level
                    questions_answered += 1

                    if monster.hp <= 0:
                        # Start death animation
                        monster.start_death_animation()

                        # Set a timer to check for death animation completion
                        pygame.time.set_timer(pygame.USEREVENT + 1,
                                              1500)  # 1.5 seconds matches death animation duration
                    else:
                        question, correct_answer = new_question()

        # Update player and monster animations
        if player:
            player.update()

        if monster:
            monster.update()

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()