import tkinter as tk
from tkinter import messagebox
import random
import copy

class ChessGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Chess Game")
        self.window.geometry("600x700")
        self.window.resizable(False, False)
        
        # Chess piece Unicode symbols
        self.pieces = {
            'white': {
                'king': '♔', 'queen': '♕', 'rook': '♖', 
                'bishop': '♗', 'knight': '♘', 'pawn': '♙'
            },
            'black': {
                'king': '♚', 'queen': '♛', 'rook': '♜', 
                'bishop': '♝', 'knight': '♞', 'pawn': '♟'
            }
        }
        
        # Game state
        self.board = self.create_initial_board()
        self.current_player = 'white'
        self.selected_square = None
        self.game_over = False
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)
        self.computer_thinking = False
        
        # Game modes
        self.auto_play_mode = False  # Computer vs Computer
        self.human_vs_computer = True  # Default: Human vs Computer
        
        # Move history for basic AI
        self.move_history = []
        
        self.create_widgets()
        
    def create_initial_board(self):
        # Create 8x8 board with initial piece positions
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Black pieces (top)
        board[0] = [('black', 'rook'), ('black', 'knight'), ('black', 'bishop'), ('black', 'queen'),
                   ('black', 'king'), ('black', 'bishop'), ('black', 'knight'), ('black', 'rook')]
        board[1] = [('black', 'pawn') for _ in range(8)]
        
        # White pieces (bottom)
        board[7] = [('white', 'rook'), ('white', 'knight'), ('white', 'bishop'), ('white', 'queen'),
                   ('white', 'king'), ('white', 'bishop'), ('white', 'knight'), ('white', 'rook')]
        board[6] = [('white', 'pawn') for _ in range(8)]
        
        return board
    
    def create_widgets(self):
        # Title
        title_label = tk.Label(self.window, text="Chess Game", 
                              font=("Arial", 24, "bold"), fg="brown")
        title_label.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(self.window, text="White to move (You)", 
                                    font=("Arial", 14), fg="blue")
        self.status_label.pack(pady=5)
        
        # Chessboard frame
        self.board_frame = tk.Frame(self.window, bg="brown")
        self.board_frame.pack(pady=10)
        
        # Create 8x8 grid of buttons
        self.buttons = []
        for i in range(8):
            button_row = []
            for j in range(8):
                # Alternate colors for chessboard pattern
                bg_color = "wheat" if (i + j) % 2 == 0 else "saddlebrown"
                btn = tk.Button(self.board_frame, text="", font=("Arial", 20),
                               width=3, height=1, bg=bg_color,
                               command=lambda r=i, c=j: self.square_clicked(r, c))
                btn.grid(row=i, column=j, padx=1, pady=1)
                button_row.append(btn)
            self.buttons.append(button_row)
        
        # Control buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)
        
        new_game_btn = tk.Button(button_frame, text="New Game", font=("Arial", 10),
                                bg="lightgreen", command=self.new_game)
        new_game_btn.grid(row=0, column=0, padx=3)
        
        # Game mode buttons
        self.auto_play_btn = tk.Button(button_frame, text="Computer vs Computer", font=("Arial", 10),
                                      bg="lightblue", command=self.toggle_auto_play)
        self.auto_play_btn.grid(row=0, column=1, padx=3)
        
        self.human_play_btn = tk.Button(button_frame, text="Human vs Computer", font=("Arial", 10),
                                       bg="lightyellow", command=self.set_human_mode)
        self.human_play_btn.grid(row=0, column=2, padx=3)
        
        quit_btn = tk.Button(button_frame, text="Quit", font=("Arial", 10),
                            bg="lightcoral", command=self.window.quit)
        quit_btn.grid(row=0, column=3, padx=3)
        
        # Move history display
        history_label = tk.Label(self.window, text="Recent moves:", font=("Arial", 10))
        history_label.pack()
        
        self.history_text = tk.Text(self.window, height=4, width=60, font=("Arial", 9))
        self.history_text.pack(pady=5)
        
        self.update_display()
    
    def update_display(self):
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece:
                    color, piece_type = piece
                    symbol = self.pieces[color][piece_type]
                    self.buttons[i][j].config(text=symbol)
                else:
                    self.buttons[i][j].config(text="")
                    
                # Reset background colors
                bg_color = "wheat" if (i + j) % 2 == 0 else "saddlebrown"
                if self.selected_square == (i, j):
                    bg_color = "yellow"
                self.buttons[i][j].config(bg=bg_color)
    
    def square_clicked(self, row, col):
        # BLOCK ALL INTERACTION if computer is thinking, game is over, or in auto-play mode
        if self.computer_thinking or self.auto_play_mode:
            return
            
        if self.game_over:
            return
            
        # In human vs computer mode, only allow interaction during white's turn
        if self.human_vs_computer and self.current_player != 'white':
            return
            
        if self.selected_square is None:
            # Select a piece - in human vs computer mode, only white pieces
            piece = self.board[row][col]
            if piece:
                if self.human_vs_computer and piece[0] != 'white':
                    return
                self.selected_square = (row, col)
                self.update_display()
        else:
            # Try to move the selected piece
            start_row, start_col = self.selected_square
            if (row, col) == self.selected_square:
                # Deselect
                self.selected_square = None
                self.update_display()
            elif self.is_valid_move(start_row, start_col, row, col):
                # Make the move
                self.make_move(start_row, start_col, row, col)
                self.selected_square = None
                self.update_display()
                
                # Trigger next move based on mode
                if not self.game_over:
                    if self.human_vs_computer and self.current_player == 'black':
                        self.start_computer_turn()
                    else:
                        # Update status for next turn
                        self.update_status_for_human_turn()
            else:
                # Invalid move, select new piece if it's valid for current mode
                piece = self.board[row][col]
                if piece and piece[0] == 'white':
                    self.selected_square = (row, col)
                else:
                    self.selected_square = None
                self.update_display()
    
    def start_computer_turn(self):
        """Start the computer's thinking process"""
        self.computer_thinking = True
        if self.auto_play_mode:
            player_name = "White Computer" if self.current_player == 'white' else "Black Computer"
            self.status_label.config(text=f"🤖 {player_name} is thinking...", fg="purple", font=("Arial", 14, "bold"))
        else:
            self.status_label.config(text="🤖 COMPUTER IS THINKING... PLEASE WAIT", fg="red", font=("Arial", 14, "bold"))
        self.window.update()  # Force UI update
        # Schedule computer move with minimal delay
        self.window.after(50, self.execute_computer_move)
    
    def execute_computer_move(self):
        """Execute the computer's move quickly"""
        if self.game_over:
            self.computer_thinking = False
            return
        
        # Quick move calculation
        best_move = self.find_computer_move()
        
        if best_move:
            start_row, start_col, end_row, end_col = best_move
            self.make_move(start_row, start_col, end_row, end_col)
            self.update_display()
        else:
            player_name = self.current_player.title()
            self.status_label.config(text=f"{player_name} has no valid moves!", fg="orange")
            self.game_over = True
        
        # Computer finished
        self.computer_thinking = False
        
        if not self.game_over:
            if self.auto_play_mode:
                # Continue auto-play
                self.window.after(1000, self.continue_auto_play)  # 1 second delay between moves
            else:
                self.status_label.config(text="Your turn! (White)", fg="blue", font=("Arial", 14))
    
    def continue_auto_play(self):
        """Continue computer vs computer play"""
        if self.auto_play_mode and not self.game_over:
            self.start_computer_turn()
        elif not self.auto_play_mode:
            self.update_status_for_human_turn()
    
    def update_status_for_human_turn(self):
        """Update status for human player's turn"""
        if self.human_vs_computer:
            if self.current_player == 'white':
                self.status_label.config(text="Your turn! (White)", fg="blue", font=("Arial", 14))
            else:
                self.status_label.config(text="Computer's turn (Black)", fg="red", font=("Arial", 14))
        else:
            # Human vs Human mode
            player_name = "White" if self.current_player == 'white' else "Black"
            self.status_label.config(text=f"{player_name}'s turn", fg="blue" if self.current_player == 'white' else "red", font=("Arial", 14))
    
    def toggle_auto_play(self):
        """Toggle computer vs computer mode"""
        if self.auto_play_mode:
            # Stop auto-play
            self.auto_play_mode = False
            self.auto_play_btn.config(text="Start Computer vs Computer", bg="lightblue")
            self.update_status_for_human_turn()
        else:
            # Start auto-play
            self.auto_play_mode = True
            self.human_vs_computer = True  # Keep in computer vs computer mode
            self.auto_play_btn.config(text="Stop Auto-Play", bg="orange")
            self.selected_square = None
            self.update_display()
            
            if not self.game_over and not self.computer_thinking:
                self.start_computer_turn()
    
    def set_human_mode(self):
        """Set human vs computer mode"""
        self.auto_play_mode = False
        self.human_vs_computer = True
        self.auto_play_btn.config(text="Start Computer vs Computer", bg="lightblue")
        self.selected_square = None
        self.update_display()
        self.update_status_for_human_turn()
    
    def find_computer_move(self):
        """Find best computer move efficiently"""
        moves = []
        
        # Find all pieces for current player and their possible moves
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece[0] == self.current_player:
                    piece_moves = self.get_piece_moves(row, col, piece[1])
                    for end_row, end_col in piece_moves:
                        if self.is_valid_move(row, col, end_row, end_col):
                            # Score this move
                            score = self.score_move(row, col, end_row, end_col)
                            moves.append((score, row, col, end_row, end_col))
        
        if not moves:
            return None
        
        # Sort by score and pick from top moves
        moves.sort(reverse=True)
        top_moves = moves[:min(3, len(moves))]
        chosen = random.choice(top_moves)
        return chosen[1:]  # Return (start_row, start_col, end_row, end_col)
    
    def get_piece_moves(self, row, col, piece_type):
        """Get possible moves for a piece type"""
        moves = []
        
        if piece_type == 'pawn':
            # Pawn direction based on color
            direction = -1 if self.board[row][col][0] == 'white' else 1
            start_rank = 6 if self.board[row][col][0] == 'white' else 1
            
            # Forward moves
            if 0 <= row + direction < 8 and not self.board[row + direction][col]:
                moves.append((row + direction, col))
                if row == start_rank and not self.board[row + 2 * direction][col]:
                    moves.append((row + 2 * direction, col))
            
            # Captures
            for dc in [-1, 1]:
                if 0 <= col + dc < 8 and 0 <= row + direction < 8:
                    target = self.board[row + direction][col + dc]
                    if target and target[0] != self.board[row][col][0]:
                        moves.append((row + direction, col + dc))
        
        elif piece_type == 'knight':
            knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
            for dr, dc in knight_moves:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    moves.append((new_row, new_col))
        
        elif piece_type == 'king':
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < 8 and 0 <= new_col < 8:
                        moves.append((new_row, new_col))
        
        else:
            # Sliding pieces
            directions = []
            if piece_type in ['rook', 'queen']:
                directions.extend([(0, 1), (0, -1), (1, 0), (-1, 0)])
            if piece_type in ['bishop', 'queen']:
                directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
            
            for dr, dc in directions:
                for i in range(1, 8):
                    new_row, new_col = row + dr * i, col + dc * i
                    if 0 <= new_row < 8 and 0 <= new_col < 8:
                        moves.append((new_row, new_col))
                        if self.board[new_row][new_col]:  # Stop at piece
                            break
                    else:
                        break
        
        return moves
    
    def score_move(self, start_row, start_col, end_row, end_col):
        """Score a move for the computer"""
        score = 1
        target = self.board[end_row][end_col]
        
        if target:  # Capture
            piece_values = {'pawn': 1, 'knight': 3, 'bishop': 3, 'rook': 5, 'queen': 9, 'king': 100}
            score += piece_values.get(target[1], 1) * 10
        
        # Center control bonus
        center_distance = max(abs(3.5 - end_row), abs(3.5 - end_col))
        score += (4 - center_distance) * 0.5
        
        return score
    
    def is_valid_move(self, start_row, start_col, end_row, end_col):
        # Basic bounds check
        if not (0 <= end_row < 8 and 0 <= end_col < 8):
            return False
            
        piece = self.board[start_row][start_col]
        if not piece:
            return False
            
        color, piece_type = piece
        target = self.board[end_row][end_col]
        
        # Can't capture own piece
        if target and target[0] == color:
            return False
        
        # Basic piece movement rules
        dr, dc = end_row - start_row, end_col - start_col
        
        if piece_type == 'pawn':
            direction = -1 if color == 'white' else 1
            start_rank = 6 if color == 'white' else 1
            
            if dc == 0:  # Moving forward
                if dr == direction and not target:
                    return True
                if start_row == start_rank and dr == 2 * direction and not target:
                    return True
            elif abs(dc) == 1 and dr == direction and target:  # Capturing
                return True
                
        elif piece_type == 'rook':
            if dr == 0 or dc == 0:
                return self.is_path_clear(start_row, start_col, end_row, end_col)
                
        elif piece_type == 'bishop':
            if abs(dr) == abs(dc):
                return self.is_path_clear(start_row, start_col, end_row, end_col)
                
        elif piece_type == 'queen':
            if dr == 0 or dc == 0 or abs(dr) == abs(dc):
                return self.is_path_clear(start_row, start_col, end_row, end_col)
                
        elif piece_type == 'knight':
            return (abs(dr) == 2 and abs(dc) == 1) or (abs(dr) == 1 and abs(dc) == 2)
            
        elif piece_type == 'king':
            return abs(dr) <= 1 and abs(dc) <= 1
            
        return False
    
    def is_path_clear(self, start_row, start_col, end_row, end_col):
        dr = 0 if end_row == start_row else (1 if end_row > start_row else -1)
        dc = 0 if end_col == start_col else (1 if end_col > start_col else -1)
        
        r, c = start_row + dr, start_col + dc
        while (r, c) != (end_row, end_col):
            if self.board[r][c] is not None:
                return False
            r, c = r + dr, c + dc
            
        return True
    
    def make_move(self, start_row, start_col, end_row, end_col):
        piece = self.board[start_row][start_col]
        captured = self.board[end_row][end_col]
        
        # Update king position
        if piece and piece[1] == 'king':
            if piece[0] == 'white':
                self.white_king_pos = (end_row, end_col)
            else:
                self.black_king_pos = (end_row, end_col)
        
        # Make the move
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None
        
        # Record move
        move_str = f"{self.current_player}: {chr(ord('a')+start_col)}{8-start_row} to {chr(ord('a')+end_col)}{8-end_row}"
        if captured:
            move_str += f" (captured {captured[1]})"
        self.move_history.append(move_str)
        
        # Update history display
        self.history_text.delete(1.0, tk.END)
        recent_moves = self.move_history[-8:]
        self.history_text.insert(tk.END, '\n'.join(recent_moves))
        
        # Check for checkmate/game end
        if captured and captured[1] == 'king':
            winner = "White" if self.current_player == 'white' else "Black"
            self.status_label.config(text=f"🎉 {winner} WINS! King captured!", fg="green", font=("Arial", 16, "bold"))
            self.game_over = True
            return
        
        # Switch turns
        self.current_player = 'black' if self.current_player == 'white' else 'white'
    
    def new_game(self):
        self.board = self.create_initial_board()
        self.current_player = 'white'
        self.selected_square = None
        self.game_over = False
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)
        self.move_history = []
        self.computer_thinking = False
        
        # Reset to human vs computer mode
        self.auto_play_mode = False
        self.human_vs_computer = True
        self.auto_play_btn.config(text="Start Computer vs Computer", bg="lightblue")
        
        self.status_label.config(text="White to move (You)", fg="blue", font=("Arial", 14))
        self.history_text.delete(1.0, tk.END)
        self.update_display()
    
    def run(self):
        self.window.mainloop()

# Create and run the game
if __name__ == "__main__":
    game = ChessGame()
    game.run()

