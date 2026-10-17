import customtkinter as ctk
import random
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

window = ctk.CTk()
window.title("x-o")
window.geometry("420x520")
window.minsize(360, 480)

game = "---------"
current_player = "X"
game_over = False
ai_player = "O"
ai_difficulty = "Medium"

header = ctk.CTkLabel(
    window,
    text="xo ai",
    font=ctk.CTkFont(family="Abadi", size=22, weight="bold"),
)
header.pack(padx=20, pady=(20, 10))

frame = ctk.CTkFrame(window)
frame.pack(padx=20, pady=10)

turn_label = ctk.CTkLabel(
    window,
    text=f"{current_player}'s turn!",
    font=ctk.CTkFont(family="Abadi", size=16),
)
turn_label.pack(pady=(0, 10))

bottom_frame = ctk.CTkFrame(window)
bottom_frame.pack(padx=20, pady=(0, 20), fill="x")

buttons = []
ai_move_button = None


def schedule_reset():
    timer = threading.Timer(2.0, reset_board)
    timer.daemon = True
    timer.start()


def get_board():
    return [[btn.cget("text") for btn in row] for row in buttons]


def refresh():
    global game

    newgame = ""
    for row_buttons in buttons:
        for btn in row_buttons:
            if btn.cget("text") == "X":
                newgame += "x"
            elif btn.cget("text") == "O":
                newgame += "o"
            else:
                newgame += "-"

    game = newgame
    print(game)


def update_ai_button_state():
    if ai_move_button is None:
        return

    if game_over or current_player == "X":
        ai_move_button.configure(state="disabled")
    else:
        ai_move_button.configure(state="normal")


def reset_board():
    global current_player, game_over

    current_player = "X"
    game_over = False
    turn_label.configure(text=f"{current_player}'s turn!")

    for row_buttons in buttons:
        for btn in row_buttons:
            btn.configure(text="")

    refresh()
    update_ai_button_state()


def winning_position(board, player):
    for row in range(3):
        if board[row][0] == player and board[row][0] == board[row][1] == board[row][2]:
            return True

    for col in range(3):
        if board[0][col] == player and board[0][col] == board[1][col] == board[2][col]:
            return True

    if board[0][0] == player and board[0][0] == board[1][1] == board[2][2]:
        return True

    if board[0][2] == player and board[0][2] == board[1][1] == board[2][0]:
        return True

    return False


def check_winner():
    board = get_board()

    for row in range(3):
        if board[row][0] != "" and board[row][0] == board[row][1] == board[row][2]:
            return board[row][0]

    for col in range(3):
        if board[0][col] != "" and board[0][col] == board[1][col] == board[2][col]:
            return board[0][col]

    if board[0][0] != "" and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]

    if board[0][2] != "" and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]

    if all(cell != "" for row in board for cell in row):
        return "draw"

    return None


def apply_move(row, col, player):
    global current_player, game_over

    btn = buttons[row][col]
    if btn.cget("text") != "":
        return False

    btn.configure(text=player)
    refresh()

    result = check_winner()

    if result == "draw":
        turn_label.configure(text="It's a draw!")
        game_over = True
        update_ai_button_state()
        schedule_reset()
        return True

    if result:
        turn_label.configure(text=f"{result} wins!")
        game_over = True
        update_ai_button_state()
        schedule_reset()
        return True

    current_player = "X" if player == "O" else "O"
    turn_label.configure(text=f"{current_player}'s turn!")
    update_ai_button_state()
    return True


def get_valid_moves():
    return [(row, col) for row in range(3) for col in range(3) if buttons[row][col].cget("text") == ""]


def choose_winning_move(board, player):
    for row, col in get_valid_moves_from_board(board):
        board[row][col] = player
        if winning_position(board, player):
            return (row, col)
        board[row][col] = ""
    return None


def get_valid_moves_from_board(board):
    return [(r, c) for r in range(3) for c in range(3) if board[r][c] == ""]


def choose_block_move(board, player):
    for row, col in get_valid_moves_from_board(board):
        board[row][col] = player
        if winning_position(board, player):
            return (row, col)
        board[row][col] = ""
    return None


def get_corner_moves():
    return [(0, 0), (0, 2), (2, 0), (2, 2)]


def get_edge_moves():
    return [(0, 1), (1, 0), (1, 2), (2, 1)]


def choose_threat_move(board, player):
    opponent = "O" if player == "X" else "X"

    for row, col in get_valid_moves_from_board(board):
        board[row][col] = player

        if choose_winning_move(board, opponent) is not None:
            board[row][col] = ""
            continue

        if choose_winning_move(board, player) is not None:
            board[row][col] = ""
            return (row, col)

        board[row][col] = ""

    return None


def choose_safe_moves(board, player):
    opponent = "O" if player == "X" else "X"
    safe_moves = []

    for row, col in get_valid_moves_from_board(board):
        board[row][col] = player
        opponent_win = choose_winning_move(board, opponent)
        board[row][col] = ""

        if opponent_win is None:
            safe_moves.append((row, col))

    return safe_moves


def choose_fork_block_move(board, player):
    human = "O" if player == "X" else "X"
    winning_lines = [
        [(0, 0), (0, 1), (0, 2)],
        [(1, 0), (1, 1), (1, 2)],
        [(2, 0), (2, 1), (2, 2)],
        [(0, 0), (1, 0), (2, 0)],
        [(0, 1), (1, 1), (2, 1)],
        [(0, 2), (1, 2), (2, 2)],
        [(0, 0), (1, 1), (2, 2)],
        [(0, 2), (1, 1), (2, 0)],
    ]

    threat_moves = []
    for line in winning_lines:
        human_count = 0
        empty_cells = []
        for row, col in line:
            cell = board[row][col]
            if cell == human:
                human_count += 1
            elif cell == "":
                empty_cells.append((row, col))

        if human_count == 2 and len(empty_cells) == 1:
            threat_moves.append(empty_cells[0])

    if not threat_moves:
        return None

    for move in get_corner_moves():
        if move in threat_moves and board[move[0]][move[1]] == "":
            return move

    return None


def choose_impossible_move():
    board = get_board()
    valid_moves = get_valid_moves_from_board(board)

    if not valid_moves:
        return None

    ai_symbol = ai_player
    human_symbol = "X" if ai_player == "O" else "O"

    ai_moves = [(r, c) for r in range(3) for c in range(3) if board[r][c] == ai_symbol]
    human_moves = [(r, c) for r in range(3) for c in range(3) if board[r][c] == human_symbol]

    ai_win = choose_winning_move(board, ai_symbol)
    if ai_win:
        return ai_win

    human_win = choose_winning_move(board, human_symbol)
    if human_win:
        return human_win

    fork_block = choose_fork_block_move(board, ai_symbol)
    if fork_block is not None:
        return fork_block

    if len(ai_moves) == 0 and len(human_moves) == 0:
        return random.choice(get_corner_moves())

    if len(ai_moves) == 0 and len(human_moves) == 1:
        first_human_move = human_moves[0]

        if first_human_move == (1, 1):
            return random.choice(get_corner_moves())

        if first_human_move in get_corner_moves():
            return (1, 1)

        if first_human_move in get_edge_moves():
            return (1, 1)

        return random.choice(get_corner_moves())

    if (1, 1) in ai_moves and human_moves:
        opposite_corner_pairs = [{(0, 0), (2, 2)}, {(0, 2), (2, 0)}]
        human_corner_set = set(move for move in human_moves if move in get_corner_moves())
        ai_edge_set = set(move for move in ai_moves if move in get_edge_moves())

        if any(human_corner_set == pair for pair in opposite_corner_pairs) and not ai_edge_set:
            for edge in get_edge_moves():
                if board[edge[0]][edge[1]] == "":
                    return edge

    safe_moves = choose_safe_moves(board, ai_symbol)
    if safe_moves:
        preferred_order = get_corner_moves() + get_edge_moves() + [(1, 1)]
        for move in preferred_order:
            if move in safe_moves:
                return move

    threat_move = choose_threat_move(board, ai_symbol)
    if threat_move is not None:
        return threat_move

    for corner in get_corner_moves():
        if board[corner[0]][corner[1]] == "":
            return corner

    for edge in get_edge_moves():
        if board[edge[0]][edge[1]] == "":
            return edge

    return random.choice(valid_moves)


def choose_ai_move():
    board = get_board()
    valid_moves = get_valid_moves_from_board(board)

    if not valid_moves:
        return None

    if ai_difficulty == "Easy":
        return random.choice(valid_moves)

    if ai_difficulty == "Medium":
        ai_win = choose_winning_move(board, ai_player)
        if ai_win:
            return ai_win

        opponent = "X" if ai_player == "O" else "O"
        block = choose_winning_move(board, opponent)
        if block:
            return block

        return random.choice(valid_moves)

    if ai_difficulty == "Impossible":
        return choose_impossible_move()

    return random.choice(valid_moves)


def ai_move():
    if game_over or current_player != ai_player:
        return

    move = choose_ai_move()
    if move is None:
        return

    row, col = move
    apply_move(row, col, current_player)


def on_click(row, col):
    if game_over:
        return

    if current_player == ai_player:
        return

    btn = buttons[row][col]

    if btn.cget("text") != "":
        return

    apply_move(row, col, current_player)


for row in range(3):
    row_buttons = []
    for col in range(3):
        btn = ctk.CTkButton(
            frame,
            text="",
            font=ctk.CTkFont(family="Abadi", size=30),
            width=80,
            height=80,
            corner_radius=12,
            command=lambda r=row, c=col: on_click(r, c),
        )
        btn.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        row_buttons.append(btn)
    buttons.append(row_buttons)

ai_options = ["Easy", "Medium", "Impossible"]

button_frame = ctk.CTkFrame(bottom_frame)
button_frame.pack(fill="x")

ai_move_button = ctk.CTkButton(
    button_frame,
    text="AI Move",
    command=ai_move,
    width=120,
    height=36,
)
ai_move_button.pack(side="left", padx=(0, 10))

ai_dropdown = ctk.CTkOptionMenu(
    button_frame,
    values=ai_options,
    command=lambda value: globals().__setitem__("ai_difficulty", value),
)
ai_dropdown.pack(side="left", fill="x", expand=True)
ai_dropdown.set("Medium")

update_ai_button_state()

for i in range(3):
    frame.grid_columnconfigure(i, weight=1)
    frame.grid_rowconfigure(i, weight=1)

window.mainloop()
