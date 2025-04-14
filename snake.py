import pygame
import random
import sys
import psycopg2
from datetime import datetime

def connect():

    return psycopg2.connect(

        dbname="snake",
        user="postgres",
        password="newpassword",
        host="localhost",
        port="5433"

    )

def create_tables():
    conn = connect()
    cur = conn.cursor()

    # Создаем таблицу пользователей
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(100) PRIMARY KEY,
            level INTEGER DEFAULT 1
        )
    """)

    # Удаляем старую таблицу user_scores, если она существует
    cur.execute("DROP TABLE IF EXISTS user_scores CASCADE")
    cur.execute("""
        CREATE TABLE user_scores (
            username VARCHAR(100) PRIMARY KEY REFERENCES users(username),
            score INTEGER,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

    print("Таблицы users и user_scores успешно созданы.")

def get_or_create_user():

    conn = connect()

    cur = conn.cursor()

    username = input("Введите имя пользователя: ")

    cur.execute("SELECT level FROM users WHERE username = %s", (username,))

    result = cur.fetchone()

    if result:

        level = result[0]

        print(f"Добро пожаловать, {username}! Ваш уровень: {level}")

    else:

        cur.execute("INSERT INTO users (username) VALUES (%s)", (username,))

        conn.commit()

        level = 1

        print(f"Новый пользователь создан: {username}")

    cur.close()
    conn.close()

    return username, level

def show_user_level():

    conn = connect()

    cur = conn.cursor()

    username = input("Введите имя пользователя для проверки: ")

    cur.execute("SELECT level FROM users WHERE username = %s", (username,))

    level_result = cur.fetchone()

    cur.execute("SELECT score FROM user_scores WHERE username = %s", (username,))

    score_result = cur.fetchone()

    if level_result:

        level = level_result[0]

        score = score_result[0] if score_result else 0

        print(f"Пользователь '{username}' — уровень: {level}, очки: {score}")

    else:

        print("Пользователь не найден.")

    cur.close()
    conn.close()

def save_game(username, score):

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO user_scores (username, score, saved_at)
        VALUES (%s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (username)
        DO UPDATE SET score = EXCLUDED.score, saved_at = EXCLUDED.saved_at
    """, (username, score))

    conn.commit()
    cur.close()
    conn.close()

    print(f"Прогресс сохранён: {username} — {score} очков")


def update_level(username, new_level):

    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE users SET level = %s WHERE username = %s", (new_level, username))
    conn.commit()
    cur.close()
    conn.close()

    print(f"⬆Уровень обновлён: {username} → {new_level}")


def start_snake_game():

    pygame.init()

    WIDTH, HEIGHT = 600, 600
    CELL_SIZE = 20
    COLS = WIDTH // CELL_SIZE
    ROWS = HEIGHT // CELL_SIZE

    WHITE = (255, 255, 255)
    GREEN = (0, 200, 0)
    RED = (200, 0, 0)
    BLACK = (0, 0, 0)
    GRAY = (50, 50, 50)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake_Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    create_tables()
    username, level = get_or_create_user()

    snake = [(5, 5), (4, 5), (3, 5)]
    direction = (1, 0)
    score = 0
    speed = 10 + (level - 1) * 2

    walls = []

    for x in range(COLS):

        walls.append((x, 0))

        walls.append((x, ROWS - 1))

    for y in range(ROWS):

        walls.append((0, y))

        walls.append((COLS - 1, y))

    if level >= 2:

        for x in range(10, 20):

            walls.append((x, 10))

    if level >= 3:

        for y in range(10, 20):

            walls.append((15, y))

    def draw_game(food_pos):

        screen.fill(BLACK)

        for wall in walls:

            pygame.draw.rect(screen, GRAY, (wall[0]*CELL_SIZE, wall[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        for segment in snake:

            pygame.draw.rect(screen, GREEN, (segment[0]*CELL_SIZE, segment[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        pygame.draw.rect(screen, RED, (food_pos[0]*CELL_SIZE, food_pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        score_text = font.render(f"Score: {score}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (WIDTH - 120, 10))
        pygame.display.update()

    def get_food_position():

        while True:

            x = random.randint(1, COLS - 2)

            y = random.randint(1, ROWS - 2)

            if (x, y) not in snake and (x, y) not in walls:

                return (x, y)

    def show_game_over_screen():

        screen.fill(BLACK)

        game_over_text = font.render("Game Over!", True, RED)

        score_text = font.render(f"Final Score: {score}", True, WHITE)

        level_text = font.render(f"Level Reached: {level}", True, WHITE)

        hint_text = font.render("Press ESC to quit...", True, GRAY)

        screen.blit(game_over_text, (WIDTH // 2 - 80, HEIGHT // 2 - 60))
        screen.blit(score_text, (WIDTH // 2 - 80, HEIGHT // 2 - 20))
        screen.blit(level_text, (WIDTH // 2 - 80, HEIGHT // 2 + 20))
        screen.blit(hint_text, (WIDTH // 2 - 100, HEIGHT // 2 + 60))

        pygame.display.update()

        waiting = True

        while waiting:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:

                        waiting = False

    food = get_food_position()
    running = True
    paused = False

    while running:

        clock.tick(speed)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                save_game(username, score)
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_p:

                    paused = not paused

                    if paused:

                        save_game(username, score)

                    else:

                        print("Продолжение игры")

        if paused:

            continue

        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP] and direction != (0, 1):

            direction = (0, -1)

        elif keys[pygame.K_DOWN] and direction != (0, -1):

            direction = (0, 1)

        elif keys[pygame.K_LEFT] and direction != (1, 0):

            direction = (-1, 0)

        elif keys[pygame.K_RIGHT] and direction != (-1, 0):

            direction = (1, 0)

        new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        if new_head in walls or new_head in snake:

            show_game_over_screen()
            save_game(username, score)
            pygame.quit()
            sys.exit()

        snake.insert(0, new_head)

        if new_head == food:

            score += 1

            food = get_food_position()

            if score % 5 == 0:

                level += 1
                speed += 2

                update_level(username, level)
        else:

            snake.pop()

        draw_game(food)

def menu():

    while True:

        print("\nGAME MENU")
        print("1. Создать таблицы")
        print("2. Запустить игру")
        print("3. Показать уровень пользователя")
        print("0. Выход")

        choice = input("Выберите действие: ")

        if choice == "1":

            create_tables()

        elif choice == "2":

            start_snake_game()

        elif choice == "3":

            show_user_level()

        elif choice == "0":

            print("До свидания!")

            break

        else:

            print("Неверный ввод. Попробуйте снова.")

if __name__ == "__main__":
    
    menu()