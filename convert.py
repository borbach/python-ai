import os
import sys
from tkinter import filedialog, messagebox
import tkinter as tk
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF is not installed. Please install it using: pip install PyMuPDF")
    sys.exit(1)

def select_pdf_file():
    """Open a file dialog to select a PDF file."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    file_path = filedialog.askopenfilename(
        title="Select a PDF file to convert",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )
    
    root.destroy()
    return file_path

def convert_pdf_to_jpg(pdf_path, output_dir=None, dpi=150):
    """
    Convert PDF to JPG images.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str): Directory to save JPG files (optional)
        dpi (int): Resolution for the output images
    
    Returns:
        list: List of created JPG file paths
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Set output directory
    if output_dir is None:
        output_dir = os.path.dirname(pdf_path)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get the base filename without extension
    base_name = Path(pdf_path).stem
    
    created_files = []
    
    try:
        # Open the PDF
        pdf_document = fitz.open(pdf_path)
        
        print(f"Converting PDF with {pdf_document.page_count} pages...")
        
        # Convert each page
        for page_num in range(pdf_document.page_count):
            # Get the page
            page = pdf_document[page_num]
            
            # Create a matrix for the desired DPI
            # Default is 72 DPI, so we scale by dpi/72
            zoom = dpi / 72.0
            matrix = fitz.Matrix(zoom, zoom)
            
            # Render page to an image
            pix = page.get_pixmap(matrix=matrix)
            
            # Generate output filename
            if pdf_document.page_count == 1:
                output_filename = f"{base_name}.jpg"
            else:
                output_filename = f"{base_name}_page_{page_num + 1:03d}.jpg"
            
            output_path = os.path.join(output_dir, output_filename)
            
            # Save the image
            pix.save(output_path)
            created_files.append(output_path)
            
            print(f"Converted page {page_num + 1}/{pdf_document.page_count} -> {output_filename}")
        
        # Close the PDF
        pdf_document.close()
        
        return created_files
        
    except Exception as e:
        raise Exception(f"Error converting PDF: {str(e)}")

def main():
    """Main function to run the PDF to JPG converter."""
    print("PDF to JPG Converter")
    print("=" * 30)
    
    # Select PDF file
    print("Please select a PDF file to convert...")
    pdf_file = select_pdf_file()
    
    if not pdf_file:
        print("No file selected. Exiting...")
        return
    
    print(f"Selected file: {pdf_file}")
    
    # Ask user for output directory (optional)
    root = tk.Tk()
    root.withdraw()
    
    choice = messagebox.askyesno(
        "Output Directory", 
        "Do you want to choose a different output directory?\n\n"
        "Click 'No' to save in the same folder as the PDF."
    )
    
    output_dir = None
    if choice:
        output_dir = filedialog.askdirectory(title="Select output directory")
        if not output_dir:
            output_dir = None
    
    root.destroy()
    
    try:
        # Convert PDF to JPG
        created_files = convert_pdf_to_jpg(pdf_file, output_dir, dpi=150)
        
        print(f"\nConversion completed successfully!")
        print(f"Created {len(created_files)} image(s):")
        for file_path in created_files:
            print(f"  - {file_path}")
        
        # Show success message
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(
            "Conversion Complete", 
            f"Successfully converted PDF to {len(created_files)} JPG image(s)!\n\n"
            f"Files saved to:\n{output_dir or os.path.dirname(pdf_file)}"
        )
        root.destroy()
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"\n{error_msg}")
        
        # Show error message
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Conversion Error", error_msg)
        root.destroy()

if __name__ == "__main__":
    main()


