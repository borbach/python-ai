from PIL import Image, ImageTk
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, messagebox

class HologramGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hologram Generator")
        
        self.image_paths = []
        self.composite_image = None
        
        self.create_widgets()
    
    def create_widgets(self):
        # File selection button
        self.select_button = tk.Button(self.root, text="Select JPG Files", command=self.select_files)
        self.select_button.pack(pady=10)
        
        # Hologram name input field
        self.name_label = tk.Label(self.root, text="Hologram Name:")
        self.name_label.pack()
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack(pady=5)
        
        # Generate hologram button
        self.generate_button = tk.Button(self.root, text="Generate Hologram", command=self.generate_hologram)
        self.generate_button.pack(pady=10)
        
        # Exit button
        self.exit_button = tk.Button(self.root, text="Exit", command=self.root.quit)
        self.exit_button.pack(pady=10)
        
        # Image display area
        self.image_label = tk.Label(self.root)
        self.image_label.pack()
    
    def select_files(self):
        file_paths = filedialog.askopenfilenames(title="Select JPG Files", filetypes=[("JPG files", "*.jpg *.jpeg")])
        if file_paths:
            self.image_paths = list(file_paths)
            messagebox.showinfo("Selection Complete", f"Selected {len(self.image_paths)} image(s).")
    
    def generate_hologram(self):
        if not self.image_paths:
            messagebox.showerror("Error", "Please select JPG files first.")
            return
        
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a hologram name.")
            return
        
        try:
            composite_array = np.zeros_like(np.array(Image.open(self.image_paths[0]).convert("RGB"), dtype=np.float64))
            
            for path in self.image_paths:
                img = Image.open(path).convert("RGB")
                arr = np.array(img, dtype=np.float64)
                composite_array += arr
            
            composite_array /= len(self.image_paths)
            composite_array = np.clip(composite_array, 0, 255).astype(np.uint8)
            
            self.composite_image = Image.fromarray(composite_array)
            self.display_hologram()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def display_hologram(self):
        if self.composite_image is not None:
            img_tk = ImageTk.PhotoImage(self.composite_image)
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk

if __name__ == "__main__":
    root = tk.Tk()
    app = HologramGeneratorApp(root)
    root.mainloop()

