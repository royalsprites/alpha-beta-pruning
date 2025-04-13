import tkinter as tk
import copy
import random

CELL_SIZE = 80
BOARD_SIZE = 8

class Piece:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color

class Board:
    def __init__(self, human_color):
        self.grid = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.human_color = human_color
        self.setup_pieces()

    def setup_pieces(self):
        if self.human_color == "white":
            for row in range(3):
                for col in range(BOARD_SIZE):
                    if (row + col) % 2 == 1:
                        self.grid[row][col] = Piece(row, col, "black")
            for row in range(5, 8):
                for col in range(BOARD_SIZE):
                    if (row + col) % 2 == 1:
                        self.grid[row][col] = Piece(row, col, "white")
        else:
            for row in range(3):
                for col in range(BOARD_SIZE):
                    if (row + col) % 2 == 1:
                        self.grid[row][col] = Piece(row, col, "white")
            for row in range(5, 8):
                for col in range(BOARD_SIZE):
                    if (row + col) % 2 == 1:
                        self.grid[row][col] = Piece(row, col, "black")

    def get_valid_moves(self, color, start=None, is_capture=False):
        moves = []
        direction = -1 if color == "white" else 1
        opponent = "black" if color == "white" else "white"

        check_positions = [start] if start else [
            (r, c) for r in range(BOARD_SIZE)
            for c in range(BOARD_SIZE)
            if self.grid[r][c] and self.grid[r][c].color == color
        ]

        for row, col in check_positions:
            for dx in [-2, 2]:
                new_row = row + direction * 2
                new_col = col + dx
                mid_row = row + direction
                mid_col = col + dx // 2

                if (0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE and
                        self.grid[mid_row][mid_col] and self.grid[mid_row][mid_col].color == opponent and
                        not self.grid[new_row][new_col]):

                    move = [(row, col), (new_row, new_col)]
                    moves.append(move)

                    temp_board = self.clone()
                    temp_board.move_piece(move[0], move[1])
                    additional_moves = temp_board.get_valid_moves(color, start=(new_row, new_col), is_capture=True)
                    for add_move in additional_moves:
                        moves.append([(row, col)] + add_move[1:])

            if not is_capture and not any(abs(m[0][0] - m[1][0]) == 2 for m in moves):
                for dx in [-1, 1]:
                    new_row = row + direction
                    new_col = col + dx
                    if (0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE and
                            not self.grid[new_row][new_col]):
                        moves.append([(row, col), (new_row, new_col)])

        return moves

    def move_piece(self, start, end):
        piece = self.grid[start[0]][start[1]]
        self.grid[start[0]][start[1]] = None
        piece.row, piece.col = end
        self.grid[end[0]][end[1]] = piece

        if abs(end[0] - start[0]) == 2:
            mid_row = (start[0] + end[0]) // 2
            mid_col = (start[1] + end[1]) // 2
            self.grid[mid_row][mid_col] = None

    def evaluate(self):
        score = 0
        for row in self.grid:
            for piece in row:
                if piece:
                    score += 1 if piece.color == "black" else -1
        return score

    def is_game_over(self):
        white_moves = self.get_valid_moves("white")
        black_moves = self.get_valid_moves("black")
        white_count = sum(1 for row in self.grid for piece in row if piece and piece.color == "white")
        black_count = sum(1 for row in self.grid for piece in row if piece and piece.color == "black")

        if not white_moves or white_count == 0:
            return "black"
        if not black_moves or black_count == 0:
            return "white"
        return None

    def clone(self):
        return copy.deepcopy(self)

class Game:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Checkers Game")

        self.status_label = tk.Label(self.window, text="", font=('Arial', 14))
        self.status_label.pack()

        self.canvas = tk.Canvas(self.window, width=CELL_SIZE * BOARD_SIZE, height=CELL_SIZE * BOARD_SIZE)
        self.canvas.pack()

        self.human_color = "white"  # Always the human plays as White
        self.ai_color = "black"  # AI always plays as Black
        self.board = Board(self.human_color)
        self.current_turn = "white"  # Human starts (White's turn)
        self.selected_piece = None
        self.turn_count = 0

        self.canvas.bind("<Button-1>", self.on_click)
        self.update_status()
        self.draw_board()

        if self.current_turn != self.human_color:
            self.window.after(100, self.play_ai_turn)

        self.window.mainloop()


    def draw_board(self):
        self.canvas.delete("all")
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x0 = col * CELL_SIZE
                y0 = row * CELL_SIZE
                x1 = x0 + CELL_SIZE
                y1 = y0 + CELL_SIZE
                fill = "#D18B47" if (row + col) % 2 else "#FFCE9E"
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill)

                piece = self.board.grid[row][col]
                if piece:
                    outline = "red" if (row, col) == self.selected_piece else "black"
                    self.canvas.create_oval(
                        x0 + 5, y0 + 5, x1 - 5, y1 - 5,
                        fill=piece.color,
                        outline=outline,
                        width=2
                    )

        if self.selected_piece:
            valid_moves = self.board.get_valid_moves(self.human_color, start=self.selected_piece)
            for move in valid_moves:
                end_row, end_col = move[-1]
                x0 = end_col * CELL_SIZE + CELL_SIZE // 4
                y0 = end_row * CELL_SIZE + CELL_SIZE // 4
                x1 = x0 + CELL_SIZE // 2
                y1 = y0 + CELL_SIZE // 2
                self.canvas.create_oval(x0, y0, x1, y1, fill="green", outline="green")

    def update_status(self):
        if self.current_turn == "white":
            text = "White's turn"
            color = "black" if self.human_color == "white" else "white"
        else:
            text = "Black's turn"
            color = "black" if self.human_color == "black" else "white"
        self.status_label.config(text=text, fg=color)

    def show_game_over(self, winner):
        if winner == self.human_color:
            message = "Congratulations! You win!"
        else:
            message = "Game over! AI wins!"
        self.status_label.config(text=message, fg="red")
        self.canvas.unbind("<Button-1>")

    def on_click(self, event):
        if self.current_turn != self.human_color:
            return

        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE

        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            return

        piece = self.board.grid[row][col]

        if self.selected_piece is None:
            if piece and piece.color == self.human_color:
                self.selected_piece = (row, col)
                self.draw_board()
        else:
            valid_moves = self.board.get_valid_moves(self.human_color, start=self.selected_piece)
            for valid_move in valid_moves:
                if (row, col) in valid_move[1:]:
                    index = valid_move.index((row, col))
                    selected_path = valid_move[:index + 1]
                    self.perform_human_move(selected_path)
                    return

            if piece and piece.color == self.human_color:
                self.selected_piece = (row, col)
            else:
                self.selected_piece = None
            self.draw_board()

    def perform_human_move(self, move_sequence):
        for i in range(len(move_sequence) - 1):
            self.board.move_piece(move_sequence[i], move_sequence[i + 1])

        last_pos = move_sequence[-1]
        additional_moves = self.board.get_valid_moves(self.human_color, start=last_pos, is_capture=True)
        if additional_moves:
            self.selected_piece = last_pos
            self.draw_board()
        else:
            self.selected_piece = None
            self.current_turn = self.ai_color  # After the human's move, it’s AI's turn
            self.turn_count += 1
            result = self.board.is_game_over()
            if result:
                self.show_game_over(result)
            else:
                self.update_status()
                self.draw_board()
                self.window.after(500, self.play_ai_turn)


    def play_ai_turn(self):
        valid_moves = self.board.get_valid_moves(self.ai_color)
        if not valid_moves:
            if self.turn_count > 0:
                self.show_game_over(self.human_color)
            return

        best_move = random.choice(valid_moves)
        self.board.move_piece(*best_move)
        self.current_turn = self.human_color
        self.turn_count += 1
        self.draw_board()
        self.update_status()

        # Now we check for game over
        winner = self.board.is_game_over()
        if winner:
            self.show_game_over(winner)

    def alpha_beta(self, board, depth, alpha, beta, maximizing):
        if depth == 0 or board.is_game_over():
            return None, board.evaluate()

        color = "black" if maximizing else "white"
        valid_moves = board.get_valid_moves(color)
        if not valid_moves:
            return None, board.evaluate()

        best_move = None

        if maximizing:
            max_eval = -float('inf')
            for move in valid_moves:
                new_board = board.clone()
                for i in range(len(move) - 1):
                    new_board.move_piece(move[i], move[i + 1])
                _, eval = self.alpha_beta(new_board, depth - 1, alpha, beta, False)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return best_move, max_eval
        else:
            min_eval = float('inf')
            for move in valid_moves:
                new_board = board.clone()
                for i in range(len(move) - 1):
                    new_board.move_piece(move[i], move[i + 1])
                _, eval = self.alpha_beta(new_board, depth - 1, alpha, beta, True)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return best_move, min_eval

if __name__ == "__main__":
    Game()
