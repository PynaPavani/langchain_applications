import random
import os
import time
import logging
import threading
import google.generativeai as googleai
import pygame
from dotenv import load_dotenv

load_dotenv()

# Set your Google API key
googleai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 640, 480
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Single Player Ping Pong")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Paddle dimensions
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 60

# Ball dimensions
BALL_RADIUS = 10

# Initial game state
ball_pos = [320, 240]
ball_vel = [random.choice([5, -5]), random.choice([5, -5])]
player_paddle = [50, 200]
ai_paddle = [590, 200]
scores = [0, 0]

ai_target_pos = ai_paddle[1]
lock = threading.Lock()

def draw_game():
    WIN.fill(BLACK)
    pygame.draw.circle(WIN, WHITE, ball_pos, BALL_RADIUS)
    pygame.draw.rect(WIN, WHITE, (player_paddle[0], player_paddle[1], PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.rect(WIN, WHITE, (ai_paddle[0], ai_paddle[1], PADDLE_WIDTH, PADDLE_HEIGHT))
    draw_scores()
    pygame.display.update()

def draw_scores():
    font = pygame.font.Font(None, 36)
    player_score_text = font.render(str(scores[0]), True, WHITE)
    ai_score_text = font.render(str(scores[1]), True, WHITE)
    WIN.blit(player_score_text, (WIDTH // 4, 20))
    WIN.blit(ai_score_text, (3 * WIDTH // 4, 20))

def update_ball():
    global ball_pos, ball_vel, scores

    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # Check for collision with walls
    if ball_pos[1] <= 0 or ball_pos[1] >= HEIGHT:
        ball_vel[1] = -ball_vel[1]

    # Check for collision with paddles
    if player_paddle[1] < ball_pos[1] < player_paddle[1] + PADDLE_HEIGHT:
        if ball_pos[0] - BALL_RADIUS <= player_paddle[0] + PADDLE_WIDTH:
            ball_vel[0] = -ball_vel[0]
            ball_pos[0] = player_paddle[0] + PADDLE_WIDTH + BALL_RADIUS  # Adjust ball position
            logging.info(f"Ball hit player paddle: {ball_pos}")

    if ai_paddle[1] < ball_pos[1] < ai_paddle[1] + PADDLE_HEIGHT:
        if ball_pos[0] + BALL_RADIUS >= ai_paddle[0]:
            ball_vel[0] = -ball_vel[0]
            ball_pos[0] = ai_paddle[0] - BALL_RADIUS  # Adjust ball position
            logging.info(f"Ball hit AI paddle: {ball_pos}")

    # Check for scoring
    if ball_pos[0] <= 0:
        scores[1] += 1
        logging.info(f"AI scores! Scores: {scores}")
        reset_ball()
    elif ball_pos[0] >= WIDTH:
        scores[0] += 1
        logging.info(f"Player scores! Scores: {scores}")
        reset_ball()

def reset_ball():
    global ball_pos, ball_vel
    ball_pos = [320, 240]
    ball_vel = [random.choice([5, -5]), random.choice([5, -5])]
    logging.info(f"Ball reset to: {ball_pos}")

def get_ai_move():
    global ai_target_pos
    try:
        prompt = (
            "You are an AI playing ping pong. Respond with only the new Y-coordinate for the AI paddle's position as a number.\n"
            f"The ball is at {ball_pos} and the AI paddle is at {ai_paddle}. What should be the new Y-coordinate for the AI paddle?"
        )
        logging.info(f"Calling Google API with prompt: {prompt}")
        response = googleai.chat(prompt)
        ai_move_str = response.response.strip()
        logging.info(f"Google API response: {ai_move_str}")
        ai_move = int(ai_move_str)  # Directly parse the response to an integer
        logging.info(f"Google API AI move: {ai_move}")
        with lock:
            ai_target_pos = ai_move
    except Exception as e:
        logging.error(f"Error from Google API: {e}")

def update_ai():
    global ai_target_pos
    with lock:
        target_pos = ai_target_pos

    # Heuristic: Move towards the ball
    if ball_pos[1] > ai_paddle[1] + PADDLE_HEIGHT // 2:
        ai_paddle[1] += 5
    elif ball_pos[1] < ai_paddle[1] + PADDLE_HEIGHT // 2:
        ai_paddle[1] -= 5

    # Apply Google API target position
    if target_pos > ai_paddle[1] + PADDLE_HEIGHT // 2:
        ai_paddle[1] += 3
    elif target_pos < ai_paddle[1] + PADDLE_HEIGHT // 2:
        ai_paddle[1] -= 3

    ai_paddle[1] = max(min(ai_paddle[1], HEIGHT - PADDLE_HEIGHT), 0)
    logging.info(f"AI paddle updated to: {ai_paddle[1]}")

def main():
    clock = pygame.time.Clock()
    run = True
    last_call_time = time.time()
    gpt4_interval = 2  # Call Google API every 2 seconds
    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and player_paddle[1] > 0:
            player_paddle[1] -= 5
        if keys[pygame.K_DOWN] and player_paddle[1] < HEIGHT - PADDLE_HEIGHT:
            player_paddle[1] += 5

        update_ball()
        update_ai()
        draw_game()

        current_time = time.time()
        if current_time - last_call_time > gpt4_interval:
            threading.Thread(target=get_ai_move).start()
            last_call_time = current_time

    pygame.quit()

if __name__ == "__main__":
    main()
