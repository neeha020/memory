import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import time
import threading
import winsound
import os

# Global variables
symbols_pool = ['🍎', '🍌', '🍇', '🍓', '🍍', '🥝', '🍒', '🍉', '🍑', '🍊', '🥥', '🍋',
                '🥭', '🍈', '🍏', '🍅', '🥬', '🌽', '🌶️', '🥑', '🥔', '🍄', '🍆', '🥦']

cards = []
flipped = []
matched = []
buttons = []
moves = 0
time_left = 90
timer_running = False
player_name = "Player"
rows, cols = 4, 4
theme = "dark"
fullscreen = False

score_file = "memory_game_scores.txt"

# --- SOUND ---
def play_sound(effect="flip"):
    try:
        if effect == "flip":
            winsound.MessageBeep()
        elif effect == "match":
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        elif effect == "win":
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
        elif effect == "fail":
            winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
    except:
        pass

# --- GUI SETUP ---
root = tk.Tk()
root.title("🧠 Memory Card Match Game")
root.geometry("750x800")
root.resizable(False, False)

# --- Theme Colors ---
themes = {
    "dark": {"bg": "#1e1e1e", "btn": "#444", "text": "white"},
    "light": {"bg": "#eeeeee", "btn": "#dddddd", "text": "black"},
}

# --- Theme Toggle ---
def toggle_theme():
    global theme
    theme = "light" if theme == "dark" else "dark"
    apply_theme()

# --- Fullscreen ---
def toggle_fullscreen(event=None):
    global fullscreen
    fullscreen = not fullscreen
    root.attributes("-fullscreen", fullscreen)

def exit_fullscreen(event=None):
    global fullscreen
    fullscreen = False
    root.attributes("-fullscreen", False)

# --- Theme Apply ---
def apply_theme():
    colors = themes[theme]
    root.configure(bg=colors["bg"])
    top_frame.config(bg=colors["bg"])
    game_frame.config(bg=colors["bg"])
    for widget in top_frame.winfo_children():
        widget.config(bg=colors["bg"], fg=colors["text"])
    for btn in buttons:
        btn.config(bg=colors["btn"], fg=colors["text"])

# --- Top Frame ---
top_frame = tk.Frame(root)
top_frame.pack(pady=10)

player_label = tk.Label(top_frame, text="👤 Player: ", font=('Arial', 12))
player_label.grid(row=0, column=0, padx=5)

timer_label = tk.Label(top_frame, text="⏳ Time Left: 90s", font=('Arial', 12))
timer_label.grid(row=0, column=1, padx=10)

moves_label = tk.Label(top_frame, text="🔁 Moves: 0", font=('Arial', 12))
moves_label.grid(row=0, column=2, padx=10)

restart_btn = tk.Button(top_frame, text="🔄 Restart", font=('Arial', 10), command=lambda: restart_game())
restart_btn.grid(row=0, column=3, padx=10)

theme_btn = tk.Button(top_frame, text="🌓 Theme", font=('Arial', 10), command=lambda: toggle_theme())
theme_btn.grid(row=0, column=4, padx=10)

fullscreen_btn = tk.Button(top_frame, text="🗖 Fullscreen", font=('Arial', 10), command=toggle_fullscreen)
fullscreen_btn.grid(row=0, column=5, padx=10)

# --- Game Frame ---
game_frame = tk.Frame(root)
game_frame.pack(pady=10)

# --- Flip Logic ---
def flip_card(i):
    global moves
    if i in matched or i in flipped or len(flipped) == 2:
        return
    buttons[i].config(text=cards[i], state='disabled', bg="#333")
    play_sound("flip")
    flipped.append(i)
    if len(flipped) == 2:
        moves += 1
        moves_label.config(text=f"🔁 Moves: {moves}")
        root.after(500, check_match)

# --- Match Check ---
def check_match():
    global flipped, matched
    i1, i2 = flipped
    if cards[i1] == cards[i2]:
        matched.extend([i1, i2])
        buttons[i1].config(bg='green')
        buttons[i2].config(bg='green')
        play_sound("match")
    else:
        buttons[i1].config(text='', state='normal', bg=themes[theme]["btn"])
        buttons[i2].config(text='', state='normal', bg=themes[theme]["btn"])
    flipped.clear()

    if len(matched) == len(cards):
        stop_timer()
        play_sound("win")
        show_scoreboard()

# --- Start Game ---
def start_game():
    global cards, flipped, matched, buttons, moves, time_left, timer_running
    symbols_needed = (rows * cols) // 2
    selected_symbols = symbols_pool[:symbols_needed]
    cards = selected_symbols * 2
    random.shuffle(cards)

    flipped.clear()
    matched.clear()
    buttons.clear()
    moves = 0
    time_left = {16: 90, 24: 120, 36: 150, 48: 180, 60: 210}[rows * cols]
    timer_running = False

    moves_label.config(text="🔁 Moves: 0")
    timer_label.config(text=f"⏳ Time Left: {time_left}s")

    for widget in game_frame.winfo_children():
        widget.destroy()

    for i in range(rows * cols):
        btn = tk.Button(game_frame, text='', width=5, height=3, font=('Arial', 20),
                        bg=themes[theme]["btn"], fg=themes[theme]["text"],
                        command=lambda i=i: flip_card(i))
        btn.grid(row=i // cols, column=i % cols, padx=5, pady=5)
        buttons.append(btn)

    apply_theme()
    start_timer()

def restart_game():
    stop_timer()
    start_game()

# --- Timer ---
def timer_countdown():
    global time_left, timer_running
    timer_running = True
    while time_left > 0 and len(matched) < len(cards):
        time.sleep(1)
        time_left -= 1
        timer_label.config(text=f"⏳ Time Left: {time_left}s")
    if time_left == 0 and len(matched) < len(cards):
        play_sound("fail")
        messagebox.showwarning("⏱️ Time's Up!", f"{player_name}, you ran out of time!")
        disable_all_buttons()
    timer_running = False

def start_timer():
    global timer_running
    if not timer_running:
        threading.Thread(target=timer_countdown, daemon=True).start()

def stop_timer():
    global time_left
    time_left = 0

def disable_all_buttons():
    for btn in buttons:
        btn.config(state="disabled")

# --- Scoreboard ---
def show_scoreboard():
    stars = "⭐" * (3 if moves <= (rows * cols) // 2 + 2 else 2 if moves <= (rows * cols) else 1)
    time_taken = {16: 90, 24: 120, 36: 150, 48: 180, 60: 210}[rows * cols] - time_left
    messagebox.showinfo("🎉 Game Complete!",
                        f"Player: {player_name}\nLevel: {rows}x{cols}\nMoves: {moves}\nTime: {time_taken}s\nRating: {stars}")
    save_score(player_name, rows, cols, moves, time_taken, stars)
    disable_all_buttons()

def save_score(name, r, c, moves, time_taken, stars):
    with open(score_file, "a") as f:
        f.write(f"{name},{r}x{c},{moves},{time_taken},{stars}\n")

# --- Setup Game ---
def setup_game():
    global player_name, rows, cols
    player_name = simpledialog.askstring("🎮 Enter Your Name", "What's your name?")
    if not player_name:
        player_name = "Player"
    player_label.config(text=f"👤 Player: {player_name}")

    diff = simpledialog.askstring("🎯 Difficulty",
                                  "Choose Difficulty:\nEasy (4x4)\nMedium (6x4)\nHard (6x6)\nExpert (8x6)\nMaster (10x6)")
    if diff:
        diff = diff.lower()
    if diff == "easy":
        rows, cols = 4, 4
    elif diff == "medium":
        rows, cols = 6, 4
    elif diff == "hard":
        rows, cols = 6, 6
    elif diff == "expert":
        rows, cols = 8, 6
    elif diff == "master":
        rows, cols = 10, 6
    else:
        rows, cols = 4, 4

    start_game()

# --- Exit Confirmation ---
def on_close():
    if messagebox.askokcancel("Exit", "Do you really want to quit?"):
        root.destroy()

# --- Bindings ---
root.bind("<F11>", toggle_fullscreen)
root.bind("<Escape>", exit_fullscreen)
root.bind("<Control-r>", lambda e: restart_game())
root.bind("<Control-t>", lambda e: toggle_theme())

# --- Launch Game ---
root.protocol("WM_DELETE_WINDOW", on_close)
setup_game()
root.focus_force()
root.mainloop()
