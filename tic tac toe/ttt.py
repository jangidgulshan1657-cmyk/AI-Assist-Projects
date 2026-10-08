"""Tic-tac-toe against an unbeatable computer (minimax)."""

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # columns
    (0, 4, 8), (2, 4, 6),              # diagonals
]
HUMAN = "X"
COMPUTER = "O"


def winner(board: list[str]) -> str | None:
    for a, b, c in WIN_LINES:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]
    return None


def is_full(board: list[str]) -> bool:
    return " " not in board


def minimax(board: list[str], player: str) -> int:
    """Score the position from the computer's side: +1 win, -1 loss, 0 draw."""
    w = winner(board)
    if w == COMPUTER:
        return 1
    if w == HUMAN:
        return -1
    if is_full(board):
        return 0

    other = HUMAN if player == COMPUTER else COMPUTER
    scores = []
    for i in range(9):
        if board[i] == " ":
            board[i] = player              # try the move
            scores.append(minimax(board, other))
            board[i] = " "                 # undo it
    return max(scores) if player == COMPUTER else min(scores)


def best_move(board: list[str]) -> int:
    best_score = -2
    best = -1
    for i in range(9):
        if board[i] == " ":
            board[i] = COMPUTER
            score = minimax(board, HUMAN)
            board[i] = " "
            if score > best_score:
                best_score, best = score, i
    return best


def show(board: list[str]) -> None:
    cells = [c if c != " " else str(i + 1) for i, c in enumerate(board)]
    print()
    for r in range(3):
        print("|".join(f" {c} " for c in cells[r * 3:r * 3 + 3]))
        if r < 2:
            print("---+---+---")
    print()


def human_move(board: list[str]) -> int:
    while True:
        raw = input("Your move (1-9): ").strip()
        if raw.isdecimal() and 1 <= int(raw) <= 9 and board[int(raw) - 1] == " ":
            return int(raw) - 1
        print("Pick an empty square, 1-9.")


def play() -> None:
    board = [" "] * 9
    turn = HUMAN
    while winner(board) is None and not is_full(board):
        show(board)
        if turn == HUMAN:
            board[human_move(board)] = HUMAN
        else:
            move = best_move(board)
            board[move] = COMPUTER
            print(f"Computer plays {move + 1}.")
        turn = COMPUTER if turn == HUMAN else HUMAN
    show(board)
    w = winner(board)
    print(f"{w} wins." if w else "Draw.")


if __name__ == "__main__":
    play()