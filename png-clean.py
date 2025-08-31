import cv2
import numpy as np
from PIL import Image
import os
import argparse
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

class PNGBackgroundCleaner:
    def __init__(self):
        self.current_image = None
        self.original_image = None
        self.mask = None
        self.drawing = False
        self.brush_size = 20
        self.mode = 'remove'  # 'remove' or 'keep'
        
    def load_image(self, image_path):
        """Load an image and prepare it for editing"""
        try:
            # Load image
            img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            
            if img is None:
                print(f"Error: Could not load image {image_path}")
                return False
                
            # Convert to BGRA if needed
            if len(img.shape) == 3:
                if img.shape[2] == 3:  # BGR
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
                    # Set alpha to fully opaque
                    img[:,:,3] = 255
            elif len(img.shape) == 4:  # Already BGRA
                pass
            else:
                print(f"Error: Unsupported image format")
                return False
                
            self.original_image = img.copy()
            self.current_image = img.copy()
            self.mask = np.zeros(img.shape[:2], dtype=np.uint8)
            
            print(f"Loaded image: {image_path}")
            print(f"Size: {img.shape[1]}x{img.shape[0]}")
            print(f"Channels: {img.shape[2]}")
            
            return True
            
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
    
    def auto_remove_white_background(self, threshold=240, tolerance=20):
        """Automatically remove white/light backgrounds"""
        if self.current_image is None:
            return False
            
        # Convert to RGB for processing
        rgb = cv2.cvtColor(self.current_image[:,:,:3], cv2.COLOR_BGR2RGB)
        
        # Multiple methods to detect background
        methods_masks = []
        
        # Method 1: Pure white detection
        white_mask = np.all(rgb >= threshold, axis=2)
        methods_masks.append(white_mask)
        
        # Method 2: Near-white with tolerance
        near_white = np.all(rgb >= threshold - tolerance, axis=2)
        methods_masks.append(near_white)
        
        # Method 3: Brightness-based
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        bright_mask = gray >= threshold
        methods_masks.append(bright_mask)
        
        # Method 4: Color variance (low variance = likely background)
        variance = np.var(rgb, axis=2)
        low_variance_mask = variance < 100  # Low color variance
        bright_and_uniform = bright_mask & low_variance_mask
        methods_masks.append(bright_and_uniform)
        
        # Combine methods - pixel is background if multiple methods agree
        background_mask = np.zeros_like(white_mask)
        for mask in methods_masks:
            background_mask = background_mask | mask
            
        # Clean up the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        background_mask = cv2.morphologyEx(background_mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel)
        
        # Apply flood fill from corners to get connected background
        h, w = background_mask.shape
        flood_mask = background_mask.copy()
        
        # Flood fill from all corners
        corners = [(0, 0), (0, w-1), (h-1, 0), (h-1, w-1)]
        for corner in corners:
            if background_mask[corner]:
                cv2.floodFill(flood_mask, None, corner, 255)
        
        # Set alpha channel - background becomes transparent
        self.current_image[:, :, 3] = np.where(flood_mask, 0, 255)
        
        print(f"Auto-removed background (threshold: {threshold}, tolerance: {tolerance})")
        return True
    
    def remove_black_areas(self, threshold=30):
        """Remove black/dark areas that might be unwanted background"""
        if self.current_image is None:
            return False
            
        # Convert to RGB
        rgb = cv2.cvtColor(self.current_image[:,:,:3], cv2.COLOR_BGR2RGB)
        
        # Detect dark areas
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        dark_mask = gray <= threshold
        
        # Clean up the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        dark_mask = cv2.morphologyEx(dark_mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel)
        
        # Remove small dark spots
        contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 500:  # Remove small dark spots
                cv2.fillPoly(dark_mask, [contour], 0)
        
        # Apply to alpha channel
        current_alpha = self.current_image[:, :, 3]
        new_alpha = np.where(dark_mask, 0, current_alpha)
        self.current_image[:, :, 3] = new_alpha
        
        print(f"Removed dark areas (threshold: {threshold})")
        return True
    
    def clean_edges(self, blur_radius=2):
        """Smooth the edges of the cutout"""
        if self.current_image is None:
            return False
            
        alpha = self.current_image[:, :, 3]
        
        # Blur the alpha channel slightly
        blurred_alpha = cv2.GaussianBlur(alpha, (blur_radius*2+1, blur_radius*2+1), blur_radius)
        
        self.current_image[:, :, 3] = blurred_alpha
        print(f"Cleaned edges (blur radius: {blur_radius})")
        return True
    
    def fill_holes(self, min_hole_size=100):
        """Fill small holes in the person cutout"""
        if self.current_image is None:
            return False
            
        alpha = self.current_image[:, :, 3]
        
        # Find holes (areas of 0 alpha surrounded by non-zero alpha)
        _, binary = cv2.threshold(alpha, 127, 255, cv2.THRESH_BINARY)
        
        # Find contours of holes
        inverted = cv2.bitwise_not(binary)
        contours, _ = cv2.findContours(inverted, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        holes_filled = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_hole_size:
                cv2.fillPoly(alpha, [contour], 255)
                holes_filled += 1
        
        self.current_image[:, :, 3] = alpha
        print(f"Filled {holes_filled} small holes")
        return True
    
    def create_preview_with_checkerboard(self):
        """Create a preview image with checkerboard background to show transparency"""
        if self.current_image is None:
            return None
            
        h, w = self.current_image.shape[:2]
        checkerboard = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Create checkerboard pattern
        square_size = 20
        for y in range(0, h, square_size):
            for x in range(0, w, square_size):
                color = [200, 200, 200] if ((y//square_size) + (x//square_size)) % 2 else [100, 100, 100]
                checkerboard[y:y+square_size, x:x+square_size] = color
        
        # Blend with checkerboard
        alpha = self.current_image[:, :, 3].astype(np.float32) / 255.0
        alpha_3d = np.stack([alpha, alpha, alpha], axis=2)
        
        person_bgr = self.current_image[:, :, :3].astype(np.float32)
        checkerboard = checkerboard.astype(np.float32)
        
        preview = alpha_3d * person_bgr + (1.0 - alpha_3d) * checkerboard
        return preview.astype(np.uint8)
    
    def save_image(self, output_path):
        """Save the cleaned image"""
        if self.current_image is None:
            return False
            
        try:
            cv2.imwrite(output_path, self.current_image)
            print(f"Saved cleaned image to: {output_path}")
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
    
    def process_batch(self, input_paths, output_dir, auto_settings=None):
        """Process multiple images with the same settings"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        if auto_settings is None:
            auto_settings = {
                'remove_white': True,
                'white_threshold': 240,
                'white_tolerance': 20,
                'remove_black': True,
                'black_threshold': 30,
                'clean_edges': True,
                'edge_blur': 2,
                'fill_holes': True,
                'hole_size': 100
            }
        
        results = []
        
        for input_path in input_paths:
            if not os.path.exists(input_path):
                print(f"File not found: {input_path}")
                continue
                
            print(f"\nProcessing: {input_path}")
            
            if not self.load_image(input_path):
                continue
            
            # Apply automatic cleaning
            if auto_settings['remove_white']:
                self.auto_remove_white_background(
                    auto_settings['white_threshold'],
                    auto_settings['white_tolerance']
                )
            
            if auto_settings['remove_black']:
                self.remove_black_areas(auto_settings['black_threshold'])
            
            if auto_settings['fill_holes']:
                self.fill_holes(auto_settings['hole_size'])
            
            if auto_settings['clean_edges']:
                self.clean_edges(auto_settings['edge_blur'])
            
            # Save result
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(output_dir, f"{base_name}_cleaned.png")
            
            if self.save_image(output_path):
                results.append(output_path)
                
                # Save preview
                preview = self.create_preview_with_checkerboard()
                if preview is not None:
                    preview_path = os.path.join(output_dir, f"{base_name}_preview.png")
                    cv2.imwrite(preview_path, preview)
        
        return results

def interactive_mode():
    """Interactive mode for single image processing"""
    cleaner = PNGBackgroundCleaner()
    
    # File selection
    root = tk.Tk()
    root.withdraw()
    
    input_path = filedialog.askopenfilename(
        title="Select image to clean",
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff")]
    )
    
    if not input_path:
        print("No file selected")
        return
    
    if not cleaner.load_image(input_path):
        return
    
    while True:
        print("\n" + "="*50)
        print("PNG Background Cleaner - Interactive Mode")
        print("="*50)
        print("1. Auto-remove white background")
        print("2. Remove black/dark areas")
        print("3. Fill small holes")
        print("4. Clean/smooth edges")
        print("5. Preview result")
        print("6. Save result")
        print("7. Reset to original")
        print("8. Exit")
        
        choice = input("\nSelect option (1-8): ").strip()
        
        if choice == '1':
            threshold = simpledialog.askinteger("Threshold", "White threshold (0-255):", initialvalue=240)
            tolerance = simpledialog.askinteger("Tolerance", "Tolerance:", initialvalue=20)
            if threshold and tolerance:
                cleaner.auto_remove_white_background(threshold, tolerance)
        
        elif choice == '2':
            threshold = simpledialog.askinteger("Threshold", "Black threshold (0-255):", initialvalue=30)
            if threshold is not None:
                cleaner.remove_black_areas(threshold)
        
        elif choice == '3':
            hole_size = simpledialog.askinteger("Hole Size", "Min hole size to fill:", initialvalue=100)
            if hole_size is not None:
                cleaner.fill_holes(hole_size)
        
        elif choice == '4':
            blur_radius = simpledialog.askinteger("Blur Radius", "Edge blur radius:", initialvalue=2)
            if blur_radius is not None:
                cleaner.clean_edges(blur_radius)
        
        elif choice == '5':
            preview = cleaner.create_preview_with_checkerboard()
            if preview is not None:
                cv2.imshow("Preview (checkerboard shows transparency)", preview)
                print("Press any key to close preview...")
                cv2.waitKey(0)
                cv2.destroyAllWindows()
        
        elif choice == '6':
            output_path = filedialog.asksaveasfilename(
                title="Save cleaned image",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")]
            )
            if output_path:
                cleaner.save_image(output_path)
                messagebox.showinfo("Success", f"Image saved to {output_path}")
        
        elif choice == '7':
            cleaner.current_image = cleaner.original_image.copy()
            print("Reset to original image")
        
        elif choice == '8':
            break
        
        else:
            print("Invalid option")
    
    root.destroy()

def main():
    parser = argparse.ArgumentParser(description='Clean PNG backgrounds for tourist photo composition')
    parser.add_argument('images', nargs='*', help='Input image files')
    parser.add_argument('-o', '--output', default='cleaned_images', help='Output directory')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--white-threshold', type=int, default=240, help='White background threshold')
    parser.add_argument('--white-tolerance', type=int, default=20, help='White background tolerance')
    parser.add_argument('--black-threshold', type=int, default=30, help='Black area removal threshold')
    parser.add_argument('--no-white', action='store_true', help='Skip white background removal')
    parser.add_argument('--no-black', action='store_true', help='Skip black area removal')
    parser.add_argument('--no-holes', action='store_true', help='Skip hole filling')
    parser.add_argument('--no-edges', action='store_true', help='Skip edge cleaning')
    
    args = parser.parse_args()
    
    if args.interactive or (not args.images and len(os.sys.argv) == 1):
        interactive_mode()
        return
    
    if not args.images:
        print("No input images specified")
        return
    
    # Batch processing
    cleaner = PNGBackgroundCleaner()
    
    auto_settings = {
        'remove_white': not args.no_white,
        'white_threshold': args.white_threshold,
        'white_tolerance': args.white_tolerance,
        'remove_black': not args.no_black,
        'black_threshold': args.black_threshold,
        'clean_edges': not args.no_edges,
        'edge_blur': 2,
        'fill_holes': not args.no_holes,
        'hole_size': 100
    }
    
    print("PNG Background Cleaner - Batch Mode")
    print("="*40)
    
    results = cleaner.process_batch(args.images, args.output, auto_settings)
    
    print(f"\nProcessed {len(results)} images successfully")
    print(f"Cleaned images saved to: {args.output}/")
    print("Look for *_cleaned.png and *_preview.png files")
    
    if results:
        print("\nNow you can use these cleaned images with the tourist photo composer!")

if __name__ == "__main__":
    main()


