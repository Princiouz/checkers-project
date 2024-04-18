import tkinter as tk
from tkinter import messagebox
import random
import copy


class Piece:
    def __init__(self, color, king=False):
        self.color = color
        self.king = king

    def make_king(self):
        if not self.king:
            self.king = True
            print(f"A piece has been crowned as a king!")


class Board:
    def __init__(self):
        self.board = [[None] * 8 for _ in range(8)]
        self.initialize_pieces()

    def initialize_pieces(self):
        for row in range(8):
            for col in range((row + 1) % 2, 8, 2):
                if row < 3:
                    self.board[row][col] = Piece('red')
                elif row > 4:
                    self.board[row][col] = Piece('black')

    def draw(self, canvas):
        for row in range(8):
            for col in range(8):
                x1, y1 = col * 80, row * 80
                x2, y2 = x1 + 80, y1 + 80
                fill = 'white' if (row + col) % 2 == 0 else 'gray'
                canvas.create_rectangle(x1, y1, x2, y2, fill=fill)
                piece = self.board[row][col]
                if piece:
                    color = 'red' if piece.color == 'red' else 'black'
                    outline = 'gold' if piece.king else color
                    canvas.create_oval(x1 + 10, y1 + 10, x2 - 10, y2 - 10, fill=color, outline=outline,
                                       width=2 if piece.king else 1)

    @staticmethod
    def is_within_bounds(row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def move_piece(self, start_row, start_col, end_row, end_col):
        moving_piece = self.board[start_row][start_col]
        captures = self.get_possible_captures(start_row, start_col)

        if captures:
            print("Capture available, must capture.")
            if (end_row, end_col) in captures:
                return self.handle_capture(start_row, start_col, end_row, end_col, moving_piece)
            else:
                return False, "A capture is available and must be taken."
        else:
            return self.handle_regular_move(start_row, start_col, end_row, end_col)

    def handle_regular_move(self, start_row, start_col, end_row, end_col):
        moving_piece = self.board[start_row][start_col]
        if moving_piece is None or self.board[end_row][end_col] is not None:
            return False, "Invalid move: No piece at start or destination not empty."

        if not moving_piece.king and ((moving_piece.color == 'red' and end_row < start_row) or (
                moving_piece.color == 'black' and end_row > start_row)):
            return False, "Backward moves are not allowed for non-king pieces."

        if abs(end_row - start_row) != abs(end_col - start_col):
            return False, "Moves must be diagonal."

        self.board[end_row][end_col] = moving_piece
        self.board[start_row][start_col] = None
        if (moving_piece.color == 'red' and end_row == 7) or (moving_piece.color == 'black' and end_row == 0):
            moving_piece.make_king()

        return True, "Move completed."

    def handle_capture(self, start_row, start_col, end_row, end_col, moving_piece):
        mid_row = (start_row + end_row) // 2
        mid_col = (start_col + end_col) // 2
        captured_piece = self.board[mid_row][mid_col]

        if captured_piece is None or captured_piece.color == moving_piece.color:
            return False, "Invalid capture: No opponent piece to capture."

        if not moving_piece.king:
            if (moving_piece.color == 'red' and end_row < start_row) or (
                    moving_piece.color == 'black' and end_row > start_row):
                return False, "Backward capture is not allowed for non-king pieces."

        self.board[mid_row][mid_col] = None
        self.board[end_row][end_col] = moving_piece
        self.board[start_row][start_col] = None

        if (moving_piece.color == 'red' and end_row == 7) or (moving_piece.color == 'black' and end_row == 0):
            moving_piece.make_king()

        return True, "Capture completed."

    def get_possible_moves(self, row, col, for_captures_only=False):
        piece = self.board[row][col]
        if not piece:
            return []

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        if piece.king:
            directions *= 2  # Kings can move in all diagonal directions

        possible_moves = []
        for d in directions:
            new_row, new_col = row + d[0], col + d[1]
            if self.is_within_bounds(new_row, new_col) and self.board[new_row][new_col] is None:
                if not for_captures_only:
                    possible_moves.append((new_row, new_col))

            jump_row, jump_col = row + 2 * d[0], col + 2 * d[1]
            if self.is_within_bounds(jump_row, jump_col) and self.board[jump_row][jump_col] is None:
                if self.is_within_bounds(new_row, new_col) and self.board[new_row][new_col] is not None and \
                        self.board[new_row][new_col].color != piece.color:
                    possible_moves.append((jump_row, jump_col))

        return possible_moves

    def get_possible_captures(self, row, col):
        return self.get_possible_moves(row, col, for_captures_only=True)

    def any_captures_available(self, color):
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.color == color:
                    if self.get_possible_captures(r, c):
                        return True
        return False

    def is_game_over(self):
        red_moves = self.get_all_possible_moves('red')
        black_moves = self.get_all_possible_moves('black')
        red_pieces = sum(1 for row in self.board for piece in row if piece is not None and piece.color == 'red')
        black_pieces = sum(1 for row in self.board for piece in row if piece is not None and piece.color == 'black')

        return red_pieces == 0 or black_pieces == 0 or not red_moves or not black_moves

    def evaluate(self):
        score = 0
        for row in self.board:
            for piece in row:
                if piece:
                    if piece.color == 'red':
                        score -= (3 if piece.king else 1)
                    elif piece.color == 'black':
                        score += (3 if piece.king else 1)
        return score

    def get_all_possible_moves(self, color):
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    for d in directions:
                        new_row, new_col = row + d[0], col + d[1]
                        if self.is_within_bounds(new_row, new_col) and self.board[new_row][new_col] is None:
                            moves.append((row, col, new_row, new_col))
                            print(f"Valid move from ({row}, {col}) to ({new_row}, {new_col})")
        return moves


class CheckersGame:
    def __init__(self, root_window, ai_playing=True, ai_depth=5):
        self.root = root_window
        self.board = Board()
        self.ai_playing = ai_playing
        self.ai = AI(self.board, color='black', depth=ai_depth) if self.ai_playing else None
        self.player_turn = 'red'  # Human player starts first
        self.canvas = tk.Canvas(self.root, width=640, height=640)
        self.canvas.pack()
        self.board.draw(self.canvas)
        self.canvas.bind("<ButtonPress-1>", self.on_piece_pick)
        self.canvas.bind("<B1-Motion>", self.on_piece_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_piece_drop)
        self.selected_piece = None
        self.piece_origin = None
        self.dragging_piece = None

        hint_button = tk.Button(self.root, text="Show Hint", command=self.show_hint)
        hint_button.pack(side='bottom')

    def on_piece_pick(self, event):
        col, row = event.x // 80, event.y // 80
        piece = self.board.board[row][col]
        if piece and piece.color == self.player_turn:
            self.selected_piece = (row, col)
            self.piece_origin = (event.x, event.y)
            self.show_possible_moves(row, col)

    def show_possible_moves(self, row, col):
        moves = self.board.get_possible_moves(row, col)
        captures = self.board.get_possible_captures(row, col)
        self.canvas.delete("highlight")
        for end_row, end_col in moves:
            color = "lightblue"
            if (end_row, end_col) in captures:
                color = "lightgreen"
            self.highlight_move(row, col, end_row, end_col, color)

    def highlight_move(self, start_row, start_col, end_row, end_col, color="lightgreen"):
        x1, y1 = start_col * 80, start_row * 80
        x2, y2 = end_col * 80, end_row * 80
        self.canvas.create_rectangle(x1, y1, x1 + 80, y1 + 80, fill=color, outline="black", tags="highlight")
        self.canvas.create_rectangle(x2, y2, x2 + 80, y2 + 80, fill=color, outline="black", tags="highlight")
        self.board.draw(self.canvas)
        self.root.update()

    def on_piece_drag(self, event):
        if self.selected_piece:
            self.canvas.delete(self.dragging_piece)
            x, y = event.x - 40, event.y - 40
            self.dragging_piece = self.canvas.create_oval(x, y, x + 80, y + 80, fill="red" if self.player_turn == "red" else "black")

    def on_piece_drop(self, event):
        if self.selected_piece:
            end_row, end_col = event.y // 80, event.x // 80
            success, message = self.board.move_piece(*self.selected_piece, end_row, end_col)
            if success:
                self.switch_turn()
            else:
                messagebox.showerror("Invalid Move", message)
            self.cleanup_after_move()

    def cleanup_after_move(self):
        self.selected_piece = None
        self.piece_origin = None
        self.canvas.delete(self.dragging_piece)
        self.dragging_piece = None
        self.canvas.delete("highlight")
        self.board.draw(self.canvas)

    def switch_turn(self):
        self.player_turn = 'black' if self.player_turn == 'red' else 'red'
        if self.player_turn == 'black' and self.ai_playing:
            self.root.after(500, self.ai_move)

    def show_hint(self):
        if self.selected_piece:
            row, col = self.selected_piece
            moves = self.board.get_possible_moves(row, col)
            move_str = ', '.join([f"({r}, {c})" for r, c in moves])
            messagebox.showinfo("Possible Moves", f"Possible moves from ({row}, {col}): {move_str}")

    def ai_move(self):
        best_move = self.ai.find_best_move()
        if best_move:
            self.board.move_piece(*best_move)
            self.switch_turn()
        self.board.draw(self.canvas)

    def run(self):
        self.root.mainloop()


class AI:
    def __init__(self, board, color='black', depth=5):
        self.board = board
        self.color = color
        self.depth = depth
        self.opponent_color = 'red' if color == 'black' else 'black'

    def minimax(self, node, depth, alpha, beta, maximizing_player):
        if depth == 0 or node.is_game_over():
            return node.evaluate(), []

        best_move = None
        if maximizing_player:
            max_eval = float('-inf')
            for move in node.get_all_possible_moves(self.color):
                simulation = copy.deepcopy(node)
                success, _ = simulation.move_piece(*move)
                if not success:
                    continue
                evaluation, _ = self.minimax(simulation, depth - 1, alpha, beta, False)
                if evaluation > max_eval:
                    max_eval = evaluation
                    best_move = move
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in node.get_all_possible_moves(self.opponent_color):
                simulation = copy.deepcopy(node)
                success, _ = simulation.move_piece(*move)
                if not success:
                    continue
                evaluation, _ = self.minimax(simulation, depth - 1, alpha, beta, True)
                if evaluation < min_eval:
                    min_eval = evaluation
                    best_move = move
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def find_best_move(self):
        _, best_move = self.minimax(self.board, self.depth, float('-inf'), float('inf'), True)
        return best_move

    def evaluate(self):
        # Evaluation based on piece count and kings
        red_kings, black_kings = 0, 0
        red_pieces, black_pieces = 0, 0
        for row in self.board.board:
            for piece in row:
                if piece:
                    if piece.color == 'red':
                        red_pieces += 1
                        if piece.king:
                            red_kings += 1
                    elif piece.color == 'black':
                        black_pieces += 1
                        if piece.king:
                            black_kings += 1
        score = (black_pieces - red_pieces) + (2 * (black_kings - red_kings))
        return score if self.color == 'black' else -score

    def is_game_over(self):
        # Game is over if there are no legal moves for either player
        if not self.board.get_all_possible_moves('red') and not self.board.get_all_possible_moves('black'):
            return True
        return False


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Checkers Game")
    game = CheckersGame(root)
    game.run()
