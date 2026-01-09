import sys
import pygame
import numpy as np # New
from tkinter import *
import random
import ctypes
import platform
import os
# Create a helper function
def get_path(*path_parts):
    # Finds the Absolute path to resources, whether running as a script pr as a bundled pyInstaller executable
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, *path_parts)


def dark_title_bar(window):
    if platform.system() != "Windows":
        return # Skip this if we are on Linux Mint

    """
    Tells Windows to use the dark mode title bar for this window
    """
    window.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 26
    set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ctypes.windll.user32.GetParent
    hwnd = get_parent(window.winfo_id())
    rendering_policy = ctypes.c_int(2)
    set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(rendering_policy), ctypes.sizeof(rendering_policy))

def get_high_score():
    try:
        with open("highscore.txt", "r") as file:
            return int(file.read())
    except:
        return 0

def save_high_scores(new_score):
    high_score = get_high_score()
    if new_score > high_score:
        with open("highscore.txt", "w") as file:
            file.write(str(new_score))
        high_score_label.config(text=f"High Score: {new_score}")


#--- CONSTANTS ---
GAME_WIDTH = 800
GAME_HEIGHT = 800
PANEL_HEIGHT = 60
INITIAL_SPEED = 150
MIN_SPEED = 50
SPEED_INCREMENT = 3
SPACE_SIZE = 40
BODY_PARTS = 3
SNAKE_COLOR = "#22FF00"
FOOD_COLOR = "#FF3131"
BACKGROUND_COLOR = "#1A1A1A"
GOLD_COLOR = "#FFD700"
PANEL_COLOR = "#262626"
# -- INITIALIZE AUDIO --
pygame.mixer.init()

# Use the new get_path to point to your files
eat_sound = pygame.mixer.Sound(get_path("eat.wav"))
die_sound = pygame.mixer.Sound(get_path("collision.wav"))
gold_sound = pygame.mixer.Sound(get_path("gold_apple.wav"))

# -- Initialize music
pygame.mixer.music.load(get_path("background.wav"))

#Set volume levels(0.0 to 1.0)
eat_sound.set_volume(0.5)
die_sound.set_volume(0.3)
gold_sound.set_volume(0.7)
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)

def play_sound(sound_type):
    if sound_type == "die":
        die_sound.play()

class Snake:
    def __init__(self):
        self.body_size = BODY_PARTS
        self.coordinates = []
        self.squares = []
        self.is_gold_mode = False # Track if we are glowing

        for i in range(0, BODY_PARTS):
            self.coordinates.append([0, 0])

        for i, (x, y) in enumerate(self.coordinates):
            fill_color = "#00FBFF" if i == 0 else SNAKE_COLOR
            square = canvas.create_rectangle(x, y,x + SPACE_SIZE, y + SPACE_SIZE, fill=fill_color, tag="snake")
            self.squares.append(square)

class Food:
    def __init__(self):

        x = random.randint(0, (GAME_WIDTH // SPACE_SIZE)-1) * SPACE_SIZE
        y = random.randint(0, (GAME_HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE
        self.coordinates = [x, y]

        # 10% chance to be a Golden Apple
        self.is_gold = random.random() < 0.10

        # Select color based on type
        color = GOLD_COLOR if self.is_gold else FOOD_COLOR

        canvas.create_oval(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=color, tag="food")

def start_coundown(count):
    if count > 0:
        # --Delete old text and prevent overlapping
        canvas.delete("countdown_text")
        # -- Draw the number
        canvas.create_text(GAME_WIDTH/2, GAME_HEIGHT/2, text=str(count), fill="white", font=("consolas", 80), tag="countdown_text")
        # Call this function again after 1 second with count -1
        window.after(1000, start_coundown, count - 1)
    elif count == 0:
        canvas.delete("countdown_text")
        canvas.create_text(GAME_WIDTH/2, GAME_HEIGHT/2, text="GO!", fill="#22FF00", font=("consolas", 80), tag="countdown_text")
        # Show "GO!" for half a second, then clear it and start the game
        window.after(1000, final_start)

def final_start():
    canvas.delete("countdown_text")
    next_turn(snake, food)

def show_speed_alert():
    # Create the "FAST!" text in a bright color
    canvas.create_text(GAME_WIDTH/2, 100, text="FAST!", fill="yellow", font=("consolas", 40, "bold"), tag="speed_alert")
    # Schedule it to disappear after 500 milliseconds
    window.after(500, lambda: canvas.delete("speed_alert"))

def next_turn(snake, food):
    if paused:
        return
    global direction_changed, score, current_speed
    direction_changed = False

    x, y = snake.coordinates[0]

    if direction == "up":
        y -= SPACE_SIZE
    elif direction == "down":
        y += SPACE_SIZE
    elif direction == "left":
        x -= SPACE_SIZE
    elif direction == "right":
        x += SPACE_SIZE

    snake.coordinates.insert(0, [x, y])

    # --- UPDATED! Set head color based on gold mode --
    head_color = GOLD_COLOR if snake.is_gold_mode else "#00FBFF"
    square = canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=head_color, outline="#116600")
    snake.squares.insert(0, square)

    # -- UPDATE! Set body color based on gold mode --
    body_color = GOLD_COLOR if snake.is_gold_mode else SNAKE_COLOR
    if len(snake.squares) > 1:
        canvas.itemconfig(snake.squares[1], fill=body_color)

    if x == food.coordinates[0] and y == food.coordinates[1]:
        if food.is_gold:
            gold_sound.play()
            score += 5
            snake.is_gold_mode = True # NEW: activate gold mode
        else:
            eat_sound.play()
            score += 1
            snake.is_gold_mode = False # NEW: Reset gold more

        # NEW: Immediately update the entire snake's color to the new state
        new_color = GOLD_COLOR if snake.is_gold_mode else SNAKE_COLOR
        for segment in snake.squares:
            canvas.itemconfig(segment, fill=new_color)

        current_high = get_high_score()
        if score > current_high:
            save_high_scores(score)
        if current_speed > MIN_SPEED:
            current_speed -= SPEED_INCREMENT
            # NEW: Trigger the visual alert
            show_speed_alert()

        score_label.config(text=f"Score: {score}")
        canvas.delete("food")
        food = Food() # Spawns the next one!

    else:
        del snake.coordinates[-1]
        canvas.delete(snake.squares[-1])
        del snake.squares[-1]
    if check_collisions(snake):
        play_sound("die")
        save_high_scores(score)
        game_over()
    else:
        window.after(current_speed, next_turn, snake, food)

def change_direction(new_direction):
    global direction
    global direction_changed

    if not direction_changed:
        if new_direction == 'left' and direction != 'right':
            direction = new_direction
            direction_changed = True
        elif new_direction == 'right' and direction != 'left':
            direction = new_direction
            direction_changed = True
        elif new_direction == 'up' and direction != 'down':
            direction = new_direction
            direction_changed = True
        elif new_direction == 'down' and direction != 'up':
            direction = new_direction
            direction_changed = True

def toggle_pause():
    global paused
    paused = not paused
    if not paused:
        canvas.delete("paused_text")
        next_turn(snake, food)
    else:
        canvas.create_text(GAME_WIDTH/2, GAME_HEIGHT/2, text="PAUSED", fill="white", font=("consolas", 50), tag="paused_text")

def check_collisions(snake):
    x, y = snake.coordinates[0]

    if x < 0 or x >= GAME_WIDTH or y < 0 or y >= GAME_HEIGHT:
        return True

    for body_part in snake.coordinates[1:]:
        if snake.coordinates[0] == body_part:
            return True
    return False

def game_over():
    pygame.mixer.music.stop() #stop immediately on collision

    canvas.delete(ALL)
    canvas.create_text(canvas.winfo_width()/2, canvas.winfo_height()/2 - 50, font=('consolas', 40), text="GAME OVER", fill="red", tag="gameover")
    canvas.create_text(canvas.winfo_width()/2, canvas.winfo_height()/2 + 100, font=('consolas', 20), text="press SPACE to Restart", fill="white", tag="gameover")
    window.bind('<space>', lambda event: restart_game())

def restart_game():
    global snake, food, score, direction, score_text, current_speed
    canvas.delete(ALL)
    window.unbind('<space>')

    score = 0
    current_speed = INITIAL_SPEED
    direction = "down"

    pygame.mixer.music.play(-1) #resume music on restart


    score_label.config(text=f"Score: 0")
    current_high = get_high_score()
    high_score_label.config(text=f"High Score: {get_high_score()}")
    snake = Snake()
    food = Food()
    #next_turn(snake, food)
    start_coundown(3)


# --- UI SETUP ---
window = Tk()
dark_title_bar(window)
window.title("Snake Game")
window.resizable(False, False)
window.configure(bg=BACKGROUND_COLOR)

# -- TOP PANEL
score_panel = Frame(window, bg=PANEL_COLOR, height=PANEL_HEIGHT)
score_panel.pack(fill="x")

score_label = Label(score_panel, text="Score: 0", font=("consolas", 20), bg=PANEL_COLOR, fg="white")
score_label.pack(side="left", padx=20)

high_score_label = Label(score_panel, text=f"High Score: {get_high_score()}", font=("consolas", 20), bg=PANEL_COLOR, fg="yellow")
high_score_label.pack(side="right", padx=10)

# -- GAME STATE GLOBALS
score = 0
current_speed = INITIAL_SPEED
direction = 'down'
direction_changed = False
paused = False


# -- GAME CANVAS --
canvas = Canvas(window, bg=BACKGROUND_COLOR,
                width=GAME_WIDTH, height=GAME_HEIGHT,
                highlightthickness=3,
                highlightbackground="#333333") # Dark gray border
canvas.pack()

# -- WINDOW CENTERING --
window.update()
window_width = window.winfo_width()
window_height = window.winfo_height()

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

x = int((screen_width / 2) - (window_width / 2))
y = int(max(0, (screen_height / 2) - (window_height / 2) - 40))

window.geometry(f"{window_width}x{window_height}+{x}+{y}")

snake = Snake()
food = Food()

window.bind('<Left>', lambda event: change_direction('left'))
window.bind('<Right>', lambda event: change_direction('right'))
window.bind('<Up>', lambda event: change_direction('up'))
window.bind('<Down>', lambda event: change_direction('down'))
window.bind('<p>', lambda event: toggle_pause())

#next_turn(snake, food)
start_coundown(3)
window.mainloop()