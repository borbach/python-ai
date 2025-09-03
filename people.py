#!/usr/bin/env python3
"""
Background Removal Tool
Removes background from JPG images containing people and saves as PNG with transparency.
"""

import os
import sys
from pathlib import Path

def check_and_install_dependencies():
    """Check for required packages and provide installation instructions."""
    missing_packages = []
    
    try:
        import tkinter
    except ImportError:
        print("❌ tkinter is not available!")
        print("tkinter is usually included with Python, but may need to be installed separately on some systems.")
        print("On Ubuntu/Debian: sudo apt-get install python3-tk")
        print("On CentOS/RHEL: sudo yum install tkinter")
        print("On macOS: tkinter should be included with Python")
        return False
    
    try:
        import PIL
    except ImportError:
        missing_packages.append("pillow")
    
    try:
        import numpy
    except ImportError:
        missing_packages.append("numpy")
    
    try:
        import onnxruntime
    except ImportError:
        missing_packages.append("onnxruntime")
    
    try:
        from rembg import remove
    except ImportError:
        missing_packages.append("rembg")
    
    if missing_packages:
        print("❌ Missing required packages!")
        print("\nPlease install the missing packages using one of these commands:\n")
        print("Option 1 (Recommended - includes all dependencies):")
        print("pip install rembg[gpu] pillow numpy onnxruntime")
        print("\nOption 2 (CPU only version):")
        print("pip install rembg pillow numpy onnxruntime")
        print("\nOption 3 (Install missing packages individually):")
        for package in missing_packages:
            print(f"pip install {package}")
        print(f"\nMissing: {', '.join(missing_packages)}")
        return False
    
    return True

# Check dependencies before importing
if not check_and_install_dependencies():
    sys.exit(1)

# Now import the packages
import tkinter as tk
from tkinter import filedialog, messagebox
from rembg import remove
from PIL import Image
import numpy as np

def select_input_file():
    """
    Open a file dialog to select an input image file.
    
    Returns:
        str: Path to selected file, or None if cancelled
    """
    
    # Create a root window (it will be hidden)
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    root.attributes('-topmost', True)  # Bring dialog to front
    
    # Define file types for the dialog
    filetypes = [
        ('Image files', '*.jpg *.jpeg *.png *.bmp *.tiff *.webp'),
        ('JPEG files', '*.jpg *.jpeg'),
        ('PNG files', '*.png'),
        ('All files', '*.*')
    ]
    
    try:
        # Open file dialog starting from current directory
        file_path = filedialog.askopenfilename(
            title="Select an image file",
            initialdir=os.getcwd(),
            filetypes=filetypes
        )
        
        # Clean up the root window
        root.destroy()
        
        return file_path if file_path else None
        
    except Exception as e:
        root.destroy()
        print(f"Error opening file dialog: {e}")
        return None

def select_output_file(input_path):
    """
    Open a file dialog to select where to save the output PNG file.
    
    Args:
        input_path (str): Path to input file (used for default name)
    
    Returns:
        str: Path for output file, or None if cancelled
    """
    
    # Create a root window (it will be hidden)
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    root.attributes('-topmost', True)  # Bring dialog to front
    
    # Generate default filename
    input_file = Path(input_path)
    default_name = f"{input_file.stem}_no_bg.png"
    
    try:
        # Open save dialog
        file_path = filedialog.asksaveasfilename(
            title="Save PNG file as...",
            initialdir=input_file.parent,
            initialfile=default_name,
            defaultextension=".png",
            filetypes=[
                ('PNG files', '*.png'),
                ('All files', '*.*')
            ]
        )
        
        # Clean up the root window
        root.destroy()
        
        return file_path if file_path else None
        
    except Exception as e:
        root.destroy()
        print(f"Error opening save dialog: {e}")
        return None

def remove_background(input_path, output_path=None):
    """
    Remove background from an image and save as PNG with transparency.
    
    Args:
        input_path (str): Path to input JPG file
        output_path (str): Path for output PNG file (optional)
    
    Returns:
        str: Path to the output file
    """
    
    # Validate input file
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Check if file is a valid image format
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    file_ext = Path(input_path).suffix.lower()
    if file_ext not in valid_extensions:
        raise ValueError(f"Unsupported file format: {file_ext}")
    
    # Generate output path if not provided
    if output_path is None:
        input_file = Path(input_path)
        output_path = input_file.parent / f"{input_file.stem}_no_bg.png"
    
    try:
        # Load the input image
        print(f"Loading image: {input_path}")
        with open(input_path, 'rb') as input_file:
            input_data = input_file.read()
        
        # Remove background using rembg
        print("Processing image (this may take a moment)...")
        output_data = remove(input_data)
        
        # Save the result
        print(f"Saving result to: {output_path}")
        with open(output_path, 'wb') as output_file:
            output_file.write(output_data)
        
        # Verify the output has transparency
        with Image.open(output_path) as img:
            if img.mode != 'RGBA':
                print("Warning: Output image may not have proper transparency")
            else:
                print("✓ Successfully created PNG with transparent background")
        
        return str(output_path)
        
    except Exception as e:
        raise RuntimeError(f"Error processing image: {str(e)}")

def main():
    """Main function with graphical file selection."""
    
    print("=== Background Removal Tool ===")
    print("This tool removes backgrounds from images containing people.")
    print()
    
    # Select input file using dialog
    print("Opening file selection dialog...")
    input_path = select_input_file()
    
    if not input_path:
        print("No file selected. Exiting.")
        return
    
    print(f"Selected input file: {input_path}")
    
    # Ask user if they want to choose output location
    print()
    choice = input("Do you want to choose where to save the output file? (y/n, default=n): ").strip().lower()
    
    output_path = None
    if choice in ['y', 'yes']:
        print("Opening save location dialog...")
        output_path = select_output_file(input_path)
        if not output_path:
            print("No output location selected. Using default location.")
            output_path = None
    
    try:
        # Process the image
        print("\n" + "="*50)
        result_path = remove_background(input_path, output_path)
        
        print("="*50)
        print(f"✅ SUCCESS!")
        print(f"Background removed and saved to: {result_path}")
        
        # Show file size info
        input_size = os.path.getsize(input_path) / 1024 / 1024
        output_size = os.path.getsize(result_path) / 1024 / 1024
        print(f"Original size: {input_size:.1f} MB")
        print(f"Output size: {output_size:.1f} MB")
        
        # Show success dialog
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo(
                "Success!", 
                f"Background removed successfully!\n\nSaved to:\n{result_path}"
            )
            root.destroy()
        except:
            pass  # If GUI fails, just continue
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        
        # Show error dialog
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", f"Failed to process image:\n{str(e)}")
            root.destroy()
        except:
            pass  # If GUI fails, just continue
            
        sys.exit(1)

if __name__ == "__main__":
    main()


