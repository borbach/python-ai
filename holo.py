#!/usr/bin/env python3
"""
Holographic JPG Generator
Converts a JPG image into a holographic-style image and saves it as a new JPG file
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import random
import math

class HologramGenerator:
    def __init__(self):
        # Initialize tkinter for file dialog
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window
        
    def select_image_file(self):
        """Open file dialog to select an image file"""
        file_types = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.gif"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select an image file",
            filetypes=file_types
        )
        
        return filename if filename else None
    
    def add_holographic_overlay(self, image):
        """Add holographic visual effects to the image"""
        width, height = image.size
        
        # Create overlay for holographic effects
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Add scan lines
        for y in range(0, height, 4):
            alpha = random.randint(20, 60)
            draw.line([(0, y), (width, y)], fill=(0, 255, 255, alpha), width=1)
            if y + 1 < height:
                draw.line([(0, y + 1), (width, y + 1)], fill=(0, 150, 255, alpha//2), width=1)
        
        # Add vertical interference lines
        for x in range(0, width, random.randint(15, 40)):
            alpha = random.randint(10, 30)
            draw.line([(x, 0), (x, height)], fill=(100, 200, 255, alpha), width=1)
        
        # Add random noise dots for digital artifact effect
        for _ in range(width * height // 100):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            color = random.choice([
                (0, 255, 255, random.randint(50, 150)),
                (100, 255, 255, random.randint(30, 100)),
                (255, 255, 255, random.randint(20, 80))
            ])
            draw.point((x, y), fill=color)
        
        return overlay
    
    def add_holographic_distortion(self, image):
        """Add wave distortion effect to simulate holographic instability"""
        width, height = image.size
        
        # Create distortion map
        distorted = Image.new('RGB', (width, height))
        pixels = image.load()
        distorted_pixels = distorted.load()
        
        for y in range(height):
            for x in range(width):
                # Create wave distortion
                wave_x = int(x + 3 * math.sin(y * 0.1) * math.sin(x * 0.05))
                wave_y = int(y + 2 * math.cos(x * 0.08) * math.sin(y * 0.03))
                
                # Clamp coordinates
                wave_x = max(0, min(width - 1, wave_x))
                wave_y = max(0, min(height - 1, wave_y))
                
                distorted_pixels[x, y] = pixels[wave_x, wave_y]
        
        return distorted
    
    def apply_holographic_color_grading(self, image):
        """Apply cyan/blue color grading for holographic look"""
        # Convert to numpy array for easier manipulation
        img_array = np.array(image)
        
        # Apply color matrix to shift towards cyan/blue
        color_matrix = np.array([
            [0.3, 0.4, 0.6],  # Red channel
            [0.2, 0.8, 0.9],  # Green channel  
            [0.4, 0.7, 1.2]   # Blue channel
        ])
        
        # Apply the color transformation
        img_colored = np.dot(img_array, color_matrix.T)
        
        # Clamp values to 0-255 range
        img_colored = np.clip(img_colored, 0, 255).astype(np.uint8)
        
        return Image.fromarray(img_colored)
    
    def add_glow_effect(self, image):
        """Add a glowing edge effect"""
        # Create edge detection
        edges = image.filter(ImageFilter.FIND_EDGES)
        edges = edges.filter(ImageFilter.GaussianBlur(radius=2))
        
        # Enhance the edges
        enhancer = ImageEnhance.Brightness(edges)
        edges = enhancer.enhance(2.0)
        
        # Create glow by blurring edges
        glow = edges.filter(ImageFilter.GaussianBlur(radius=5))
        
        # Blend original image with glow
        return Image.blend(image, glow, alpha=0.3)
    
    def create_hologram_effect(self, input_image):
        """Apply all holographic effects to the image"""
        print("Applying holographic effects...")
        
        # Resize if image is too large
        max_size = 1920
        if input_image.width > max_size or input_image.height > max_size:
            input_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Convert to RGB if not already
        if input_image.mode != 'RGB':
            input_image = input_image.convert('RGB')
        
        # Step 1: Apply color grading
        hologram = self.apply_holographic_color_grading(input_image)
        
        # Step 2: Add slight blur for ethereal effect
        hologram = hologram.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Step 3: Add wave distortion
        hologram = self.add_holographic_distortion(hologram)
        
        # Step 4: Add glow effect
        hologram = self.add_glow_effect(hologram)
        
        # Step 5: Enhance contrast
        enhancer = ImageEnhance.Contrast(hologram)
        hologram = enhancer.enhance(1.3)
        
        # Step 6: Add brightness variations
        enhancer = ImageEnhance.Brightness(hologram)
        hologram = enhancer.enhance(1.1)
        
        # Step 7: Create and apply overlay effects
        overlay = self.add_holographic_overlay(hologram)
        
        # Composite the overlay onto the image
        hologram = Image.alpha_composite(
            hologram.convert('RGBA'),
            overlay
        ).convert('RGB')
        
        return hologram
    
    def generate_hologram_image(self, input_path, output_path=None):
        """Main function to generate holographic image"""
        try:
            # Load the input image
            print(f"Loading image: {input_path}")
            input_image = Image.open(input_path)
            
            # Create holographic effect
            holographic_image = self.create_hologram_effect(input_image)
            
            # Generate output filename if not provided
            if output_path is None:
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                output_path = f"{base_name}_hologram.jpg"
            
            # Save the holographic image
            print(f"Saving holographic image to: {output_path}")
            holographic_image.save(output_path, 'JPEG', quality=95)
            
            print(f"✓ Holographic image created successfully!")
            print(f"  Input:  {input_path}")
            print(f"  Output: {output_path}")
            
            return True, output_path
            
        except FileNotFoundError:
            print(f"Error: File '{input_path}' not found.")
            return False, None
        except Exception as e:
            print(f"Error processing image: {e}")
            return False, None
    
    def run_interactive(self):
        """Interactive mode with file selection"""
        print("=" * 60)
        print("      HOLOGRAPHIC JPG GENERATOR")
        print("=" * 60)
        print()
        
        while True:
            print("Choose an option:")
            print("1. Browse and select image file")
            print("2. Enter filename manually")
            print("3. Quit")
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == '3':
                print("Goodbye!")
                break
            elif choice == '1':
                # File dialog selection
                input_path = self.select_image_file()
                if not input_path:
                    print("No file selected.")
                    continue
            elif choice == '2':
                # Manual filename entry
                input_path = input("Enter the image filename: ").strip()
                if not input_path:
                    print("Please enter a valid filename.")
                    continue
                    
                # Check if file exists
                if not os.path.exists(input_path):
                    print(f"File '{input_path}' not found.")
                    continue
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
                continue
            
            # Ask for output filename (optional)
            output_path = input("Enter output filename (press Enter for auto-generated): ").strip()
            if not output_path:
                output_path = None
            
            # Generate hologram
            print("\nGenerating holographic image...")
            success, final_output_path = self.generate_hologram_image(input_path, output_path)
            
            if success:
                # Ask if user wants to open the result
                if sys.platform.startswith('win'):
                    view_choice = input(f"\nWould you like to view the result? (y/n): ").strip().lower()
                    if view_choice == 'y':
                        os.startfile(final_output_path)
                elif sys.platform.startswith('darwin'):
                    view_choice = input(f"\nWould you like to view the result? (y/n): ").strip().lower()
                    if view_choice == 'y':
                        os.system(f'open "{final_output_path}"')
                elif sys.platform.startswith('linux'):
                    view_choice = input(f"\nWould you like to view the result? (y/n): ").strip().lower()
                    if view_choice == 'y':
                        os.system(f'xdg-open "{final_output_path}"')
                        
            print("\n" + "-" * 60 + "\n")
    
    def run_batch(self, input_files):
        """Batch processing mode"""
        print(f"Processing {len(input_files)} files...")
        
        successful = 0
        for i, input_file in enumerate(input_files, 1):
            print(f"\n[{i}/{len(input_files)}] Processing: {input_file}")
            success, output_path = self.generate_hologram_image(input_file)
            if success:
                successful += 1
        
        print(f"\nBatch processing complete!")
        print(f"Successfully processed: {successful}/{len(input_files)} files")

def main():
    """Main entry point"""
    try:
        generator = HologramGenerator()
        
        # Check command line arguments for batch processing
        if len(sys.argv) > 1:
            # Batch mode
            input_files = sys.argv[1:]
            generator.run_batch(input_files)
        else:
            # Interactive mode
            generator.run_interactive()
            
    except ImportError as e:
        print("Error: Required libraries not found.")
        print("Please install required packages with:")
        print("pip install Pillow numpy tkinter")
    except Exception as e:
        print(f"Error starting hologram generator: {e}")

if __name__ == "__main__":
    main()


