import tkinter as tk
from tkinter import messagebox
import random

class TicTacToeGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Tic-Tac-Toe")
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        
        # Game state
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"  # Human is X, Computer is O
        self.game_over = False
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title_label = tk.Label(self.window, text="Tic-Tac-Toe", 
                              font=("Arial", 24, "bold"), fg="blue")
        title_label.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(self.window, text="Your turn! Click a square to place X", 
                                    font=("Arial", 12), fg="green")
        self.status_label.pack(pady=5)
        
        # Game board frame
        self.board_frame = tk.Frame(self.window, bg="black")
        self.board_frame.pack(pady=20)
        
        # Create 3x3 grid of buttons
        self.buttons = []
        for i in range(3):
            button_row = []
            for j in range(3):
                btn = tk.Button(self.board_frame, text="", font=("Arial", 20, "bold"),
                               width=3, height=1, bg="lightgray",
                               command=lambda r=i, c=j: self.make_move(r, c))
                btn.grid(row=i, column=j, padx=2, pady=2)
                button_row.append(btn)
            self.buttons.append(button_row)
        
        # Control buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=20)
        
        new_game_btn = tk.Button(button_frame, text="New Game", font=("Arial", 12),
                                bg="lightblue", command=self.new_game)
        new_game_btn.pack(side=tk.LEFT, padx=10)
        
        quit_btn = tk.Button(button_frame, text="Quit", font=("Arial", 12),
                            bg="lightcoral", command=self.window.quit)
        quit_btn.pack(side=tk.LEFT, padx=10)
        
    def make_move(self, row, col):
        if self.game_over or self.board[row][col] != "":
            return
            
        # Human move
        self.board[row][col] = "X"
        self.buttons[row][col].config(text="X", fg="blue", state="disabled")
        
        # Check if human won
        if self.check_winner("X"):
            self.status_label.config(text="Congratulations! You won! 🎉", fg="green")
            self.game_over = True
            self.disable_all_buttons()
            return
            
        # Check for tie
        if self.is_board_full():
            self.status_label.config(text="It's a tie! 🤝", fg="orange")
            self.game_over = True
            return
            
        # Computer move
        self.status_label.config(text="Computer is thinking...", fg="red")
        self.window.update()
        self.window.after(500, self.computer_move)  # Small delay for effect
        
    def computer_move(self):
        if self.game_over:
            return
            
        # Find best move for computer
        move = self.get_best_move()
        if move:
            row, col = move
            self.board[row][col] = "O"
            self.buttons[row][col].config(text="O", fg="red", state="disabled")
            
            # Check if computer won
            if self.check_winner("O"):
                self.status_label.config(text="Computer wins! Try again! 🤖", fg="red")
                self.game_over = True
                self.disable_all_buttons()
                return
                
            # Check for tie
            if self.is_board_full():
                self.status_label.config(text="It's a tie! 🤝", fg="orange")
                self.game_over = True
                return
                
        self.status_label.config(text="Your turn! Click a square to place X", fg="green")
        
    def get_best_move(self):
        # Strategy: 1) Win if possible, 2) Block human from winning, 3) Take center, 4) Take corner, 5) Take any
        
        # 1. Check if computer can win
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == "":
                    self.board[i][j] = "O"
                    if self.check_winner("O"):
                        self.board[i][j] = ""  # Reset
                        return (i, j)
                    self.board[i][j] = ""  # Reset
                    
        # 2. Check if need to block human from winning
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == "":
                    self.board[i][j] = "X"
                    if self.check_winner("X"):
                        self.board[i][j] = ""  # Reset
                        return (i, j)
                    self.board[i][j] = ""  # Reset
                    
        # 3. Take center if available
        if self.board[1][1] == "":
            return (1, 1)
            
        # 4. Take a corner if available
        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
        available_corners = [corner for corner in corners if self.board[corner[0]][corner[1]] == ""]
        if available_corners:
            return random.choice(available_corners)
            
        # 5. Take any available spot
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == "":
                    return (i, j)
                    
        return None
        
    def check_winner(self, player):
        # Check rows
        for i in range(3):
            if all(self.board[i][j] == player for j in range(3)):
                return True
                
        # Check columns
        for j in range(3):
            if all(self.board[i][j] == player for i in range(3)):
                return True
                
        # Check diagonals
        if all(self.board[i][i] == player for i in range(3)):
            return True
        if all(self.board[i][2-i] == player for i in range(3)):
            return True
            
        return False
        
    def is_board_full(self):
        return all(self.board[i][j] != "" for i in range(3) for j in range(3))
        
    def disable_all_buttons(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(state="disabled")
                
    def new_game(self):
        # Reset game state
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.game_over = False
        
        # Reset UI
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text="", fg="black", state="normal", bg="lightgray")
                
        self.status_label.config(text="Your turn! Click a square to place X", fg="green")
        
    def run(self):
        self.window.mainloop()

# Create and run the game
if __name__ == "__main__":
    game = TicTacToeGame()
    game.run()

