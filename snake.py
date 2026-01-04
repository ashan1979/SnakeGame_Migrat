from tkinter import *
import random
import ctypes

import platform
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

#--- CONSTANTS ---
GAME_WIDTH = 800
GAME_HEIGHT = 800
INITIAL_SPEED = 120
MIN_SPEED = 50
SPEED_INCREMENT = 3
SPACE_SIZE = 40
BODY_PARTS = 3
SNAKE_COLOR = "#22FF00"
FOOD_COLOR = "#FF3131"
BACKGROUND_COLOR = "#1A1A1A"



class Snake:
    def __init__(self):
        self.body_size = BODY_PARTS
        self.coordinates = []
        self.squares = []

        for i in range(0, BODY_PARTS):
            self.coordinates.append([0, 0])

        for x, y in self.coordinates:
            square = canvas.create_rectangle(x, y,x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_COLOR, tag="snake")
            self.squares.append(square)

class Food:
    def __init__(self):

        x = random.randint(0, (GAME_WIDTH // SPACE_SIZE)-1) * SPACE_SIZE
        y = random.randint(0, (GAME_HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE

        self.coordinates = [x, y]

        canvas.create_oval(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=FOOD_COLOR, tag="food")


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

    square = canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill="#00FBFF", outline="#116600")
    snake.squares.insert(0, square)

    if len(snake.squares) > 1:
        canvas.itemconfig(snake.squares[1], fill=SNAKE_COLOR)

    if x == food.coordinates[0] and y == food.coordinates[1]:
        global score
        score += 1

        # -- Live High Score Update
        current_high = get_high_score()
        if score > current_high:
            canvas.itemconfig("h_score", text=f"high: {score}")

        #-- DIFFICULTY SCALING
        if current_speed > MIN_SPEED:
            current_speed -= SPEED_INCREMENT

        canvas.itemconfig(score_text, text="Score: {}".format(score))
        canvas.delete("food")
        food = Food()
    else:
        del snake.coordinates[-1]
        canvas.delete(snake.squares[-1])
        del snake.squares[-1]
    if check_collisions(snake):
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
    canvas.delete(ALL)
    canvas.create_text(canvas.winfo_width()/2, canvas.winfo_height()/2, font=('consolas', 40), text="GAME OVER", fill="red", tag="gameover")
    canvas.create_text(canvas.winfo_width()/2, canvas.winfo_height()/2 + 50, font=('consolas', 20), text="press SPACE to Restart", fill="white", tag="gameover")
    window.bind('<space>', lambda event: restart_game())

def restart_game():
    global snake, food, score, direction, score_text, current_speed
    canvas.delete(ALL)
    window.unbind('<space>')

    score = 0
    current_speed = INITIAL_SPEED
    direction = "down"


    score_text = canvas.create_text(10, 10, anchor="nw", text="Score: 0", fill="white", font=("consolas", 20))
    current_high = get_high_score()
    canvas.create_text(GAME_WIDTH - 1, 10, anchor="ne", text=f"High: {current_high}", fill="yellow", font=("consolas", 20), tag="h_score")
    snake = Snake()
    food = Food()
    next_turn(snake, food)

window = Tk()
dark_title_bar(window)
window.title("Snake Game")
window.resizable(False, False)
window.configure(bg=BACKGROUND_COLOR)

# -- GAME STATE GLOBALS
score = 0
current_speed = INITIAL_SPEED
direction = 'down'
direction_changed = False
paused = False



canvas = Canvas(window, bg=BACKGROUND_COLOR,
                width=GAME_WIDTH, height=GAME_HEIGHT,
                highlightthickness=3,
                highlightbackground="#333333") # Dark gray border
canvas.pack(padx=20, pady=20)

score_text = canvas.create_text(10, 10, anchor="nw", text="Score: 0", fill="white", font=("consolas", 20))
high_score_val = get_high_score()
canvas.create_text(GAME_WIDTH - 10, 10, anchor="ne", text=f"High: {get_high_score()}", fill="yellow", font=("consolas", 20), tag="h_score")

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

next_turn(snake, food)

window.mainloop()