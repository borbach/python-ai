import tkinter as tk
from tkinter import messagebox
import subprocess
import sys

class ButtonLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Einstein")
        self.root.geometry("900x700")
        self.root.configure(bg='lightgray')
        
        # Create main frame
        main_frame = tk.Frame(root, bg='lightgray', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        # Title label
        title_label = tk.Label(main_frame, text="Python Program Launcher", 
                              font=('Arial', 16, 'bold'), bg='lightgray')
        title_label.pack(pady=(0, 20))
        
        # Button configurations: (text, color, script_name)
        button_configs = [
            ("Financial Advisor", "#FF6B6B", "financial.py"),
            ("Health Advisor", "#4ECDC4", "health.py"),
            ("Launch Text Editor", "#45B7D1", "editor.py"),
            ("Launch File Manager", "#96CEB4", "utility.py"),
            ("Launch Web Server", "#FFEAA7", "server.py"),
            ("Launch Data Analyzer", "#DDA0DD", "analyzer.py"),
            ("Launch Image Processor", "#FF9F43", "image_processor.py"),
            ("Launch Music Player", "#10AC84", "music_player.py"),
            ("Launch Password Manager", "#5F27CD", "password_manager.py"),
            ("Launch System Monitor", "#00D2D3", "system_monitor.py"),
            ("Launch Backup Tool", "#FF3838", "backup_tool.py"),
            ("Launch Network Scanner", "#2F3542", "network_scanner.py"),
            ("Launch Database Manager", "#3742FA", "database_manager.py"),
            ("Launch Log Viewer", "#2ED573", "log_viewer.py"),
            ("Launch API Tester", "#FFA502", "api_tester.py"),
            ("Launch Code Formatter", "#FF6348", "code_formatter.py"),
            ("Launch File Converter", "#7BED9F", "file_converter.py"),
            ("Launch Weather App", "#70A1FF", "weather_app.py"),
            ("Launch Task Scheduler", "#5352ED", "task_scheduler.py"),
            ("Launch Email Client", "#FF4757", "email_client.py"),
            ("Launch Chat Bot", "#2F3542", "chat_bot.py"),
            ("Launch Encryption Tool", "#A4B0BE", "encryption_tool.py"),
            ("Launch Video Player", "#FF3F34", "video_player.py"),
            ("Launch Photo Gallery", "#FF9FF3", "photo_gallery.py")
        ]
        
        # Create a scrollable frame for all the buttons
        canvas = tk.Canvas(main_frame, bg='lightgray', highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='lightgray')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, pady=(0, 10))
        scrollbar.pack(side="right", fill="y", pady=(0, 10))
        
        # Create program launch buttons in a grid layout
        buttons_per_row = 3
        row = 0
        col = 0
        
        for text, color, script in button_configs:
            btn = tk.Button(scrollable_frame, text=text, bg=color, fg='white',
                           font=('Arial', 10, 'bold'), width=18, height=3,
                           relief='raised', bd=3,
                           command=lambda s=script: self.launch_program(s))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            
            # Add hover effects
            btn.bind("<Enter>", lambda e, b=btn: self.on_enter(e, b))
            btn.bind("<Leave>", lambda e, b=btn: self.on_leave(e, b))
            
            col += 1
            if col >= buttons_per_row:
                col = 0
                row += 1
        
        # Configure grid weights for proper resizing
        for i in range(buttons_per_row):
            scrollable_frame.columnconfigure(i, weight=1)
        
        # Separator frame (outside the scrollable area)
        separator_frame = tk.Frame(main_frame, bg='lightgray')
        separator_frame.pack(fill='x', pady=10)
        
        separator = tk.Frame(separator_frame, height=2, bg='gray')
        separator.pack(fill='x')
        
        # Exit button frame (outside the scrollable area, always visible)
        exit_frame = tk.Frame(main_frame, bg='lightgray')
        exit_frame.pack(fill='x')
        
        # Exit button
        exit_btn = tk.Button(exit_frame, text="EXIT APPLICATION", bg="#FF4757", fg='white',
                            font=('Arial', 14, 'bold'), width=25, height=2,
                            relief='raised', bd=4, command=self.exit_app)
        exit_btn.pack(pady=10)
        # Bind mousewheel to canvas for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux
    
    def launch_program(self, script_name):
        """Launch a Python program as a subprocess"""
        try:
            # Use sys.executable to ensure we use the same Python interpreter
            subprocess.Popen([sys.executable, script_name])
            print(f"Launched: {script_name}")
        except FileNotFoundError:
            messagebox.showerror("Error", f"Could not find {script_name}\n\n"
                               f"Make sure the file exists in the same directory as this launcher.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {script_name}\n\nError: {str(e)}")
    
    def on_enter(self, event, button):
        """Handle mouse hover enter"""
        button.configure(relief='sunken')
    
    def on_leave(self, event, button):
        """Handle mouse hover leave"""
        button.configure(relief='raised')
    
    def exit_app(self):
        """Exit the application"""
        if messagebox.askquestion("Exit", "Are you sure you want to exit?") == 'yes':
            self.root.quit()
            self.root.destroy()

def main():
    root = tk.Tk()
    app = ButtonLauncher(root)
    
    # Center the window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()


