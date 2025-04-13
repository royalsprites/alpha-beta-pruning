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
            # Place AI's black pieces at the top
            for row in range(3):
                for col in range(BOARD_SIZE):
                    if (row + col) % 2 == 1:
                        self.grid[row][col] = Piece(row, col, "black")
            # Place human's white pieces at the bottom
            for row in range(5, 8):
                for col in range(BOARD_SIZE):
                    if (row + col) % 2 == 1:
                        self.grid[row][col] = Piece(row, col, "white")
        else:
            # Place AI's white pieces at the top
            for row in range(3):
                for col in range(BOARD_SIZE):
                    if (row + col) % 2 == 1:
                        self.grid[row][col] = Piece(row, col, "white")
            # Place human's black pieces at the bottom
            for row in range(5, 8):
                for col in range(BOARD_SIZE):
                    if (row + col) % 2 == 1:
                        self.grid[row][col] = Piece(row, col, "black")

    def get_valid_moves(self, color, start=None, is_capture=False):
        moves = []
        direction = -1 if color == "white" else 1
        opponent = "black" if color == "white" else "white"

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if start and (row, col) != start:  # If a start position is specified, skip other pieces
                    continue
                piece = self.grid[row][col]
                if piece and piece.color == color:
                    # Capture moves (jump over opponent)
                    for dx in [-2, 2]:
                        new_row = row + 2 * direction
                        new_col = col + dx
                        mid_row = row + direction
                        mid_col = col + dx // 2
                        if (0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE and
                            self.grid[mid_row][mid_col] and self.grid[mid_row][mid_col].color == opponent and
                            not self.grid[new_row][new_col]):
                            moves.append(((row, col), (new_row, new_col)))

                            # Check for additional captures recursively
                            temp_board = self.clone()
                            temp_board.move_piece((row, col), (new_row, new_col))
                            additional_moves = temp_board.get_valid_moves(color, start=(new_row, new_col), is_capture=True)
                            for add_move in additional_moves:
                                moves.append(((row, col), *add_move[1:]))

                    # Normal moves (only if not in a capture chain)
                    if not is_capture:
                        for dx in [-1, 1]:
                            new_row = row + direction
                            new_col = col + dx
                            if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                                if not self.grid[new_row][new_col]:
                                    moves.append(((row, col), (new_row, new_col)))
        return moves

    def move_piece(self, start, end):
        piece = self.grid[start[0]][start[1]]
        self.grid[start[0]][start[1]] = None
        piece.row, piece.col = end
        self.grid[end[0]][end[1]] = piece

        # Check for capture
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
        return not self.get_valid_moves("white") or not self.get_valid_moves("black")

    def clone(self):
        return copy.deepcopy(self)

class Game:
    def __init__(self):
        self.window = tk.Tk()
        self.canvas = tk.Canvas(self.window, width=640, height=640)
        self.canvas.pack()
        self.human_color = random.choice(["white", "black"])
        self.ai_color = "black" if self.human_color == "white" else "white"
        self.board = Board(self.human_color)
        self.current_turn = "white"  # White always starts
        self.selected_piece = None
        self.canvas.bind("<Button-1>", self.on_click)
        self.window.title(f"Dama: Human ({self.human_color}) vs AI ({self.ai_color})")

        self.draw_board()

        # If AI gets white, let AI play first
        if self.current_turn == self.ai_color:
            self.window.after(1000, self.play_ai_turn)

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
                    color = "black" if piece.color == "black" else "white"
                    self.canvas.create_oval(x0+10, y0+10, x1-10, y1-10, fill=color)
        if self.selected_piece:
            r, c = self.selected_piece
            x0, y0 = c * CELL_SIZE, r * CELL_SIZE
            x1, y1 = x0 + CELL_SIZE, y0 + CELL_SIZE
            self.canvas.create_rectangle(x0, y0, x1, y1, outline="blue", width=3)

            # Highlight possible moves
            valid_moves = self.board.get_valid_moves(self.human_color, start=self.selected_piece)
            for _, (new_row, new_col) in valid_moves:
                x0, y0 = new_col * CELL_SIZE, new_row * CELL_SIZE
                x1, y1 = x0 + CELL_SIZE, y0 + CELL_SIZE
                self.canvas.create_oval(x0+20, y0+20, x1-20, y1-20, outline="green", width=3)

    def on_click(self, event):
        if self.current_turn != self.human_color:
            return

        row = event.y // CELL_SIZE
        col = event.x // CELL_SIZE
        piece = self.board.grid[row][col]

        if self.selected_piece is None:
            if piece and piece.color == self.human_color:
                self.selected_piece = (row, col)
                self.draw_board()
        else:
            move = (self.selected_piece, (row, col))
            if move in self.board.get_valid_moves(self.human_color):
                self.board.move_piece(*move)
                self.selected_piece = None  # Turn always ends
                self.current_turn = self.ai_color
                self.draw_board()
                self.window.after(1000, self.play_ai_turn)
            else:
                self.selected_piece = None
                self.draw_board()

    def play_ai_turn(self):
        if self.board.is_game_over():
            print("Game Over")
            return

        move, _ = self.alpha_beta(self.board, 4, -float('inf'), float('inf'), self.ai_color == "black")
        if move:
            self.board.move_piece(move[0], move[1])
        self.current_turn = self.human_color
        self.draw_board()

    def alpha_beta(self, board, depth, alpha, beta, maximizing):
        if depth == 0 or board.is_game_over():
            return None, board.evaluate()

        color = "black" if maximizing else "white"
        best_move = None
        if maximizing:
            max_eval = -float('inf')
            for move in board.get_valid_moves(color):
                new_board = board.clone()
                new_board.move_piece(move[0], move[1])
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
            for move in board.get_valid_moves(color):
                new_board = board.clone()
                new_board.move_piece(move[0], move[1])
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
