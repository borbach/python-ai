import cv2
import numpy as np
import requests
from PIL import Image, ImageEnhance, ImageFilter
import matplotlib.pyplot as plt
from io import BytesIO
import os

class TouristPhotoComposer:
    def __init__(self):
        # Use Wikimedia Commons and other free sources for tourist sites
        self.tourist_sites = [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg/800px-Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg",  # Eiffel Tower
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Clock_Tower_-_Palace_of_Westminster%2C_London_-_May_2007.jpg/600px-Clock_Tower_-_Palace_of_Westminster%2C_London_-_May_2007.jpg",  # Big Ben
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Statue_of_Liberty_7.jpg/600px-Statue_of_Liberty_7.jpg",  # Statue of Liberty
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Taj_Mahal_%28Edited%29.jpeg/800px-Taj_Mahal_%28Edited%29.jpeg",  # Taj Mahal
            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Tower_Bridge_from_Shad_Thames.jpg/800px-Tower_Bridge_from_Shad_Thames.jpg",  # Tower Bridge
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Machu_Picchu%2C_Peru.jpg/800px-Machu_Picchu%2C_Peru.jpg",  # Machu Picchu
            "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Sydney_Opera_House_-_Dec_2008.jpg/800px-Sydney_Opera_House_-_Dec_2008.jpg",  # Sydney Opera House
            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Sagrada_Familia_01.jpg/600px-Sagrada_Familia_01.jpg",  # Sagrada Familia
            "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/GoldenGateBridge-001.jpg/800px-GoldenGateBridge-001.jpg",  # Golden Gate Bridge
            "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Vd-Orig.jpg/800px-Vd-Orig.jpg",  # Neuschwanstein Castle
            "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Colosseo_2020.jpg/800px-Colosseo_2020.jpg",  # Colosseum
            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Brooklyn_Bridge_Manhattan.jpg/800px-Brooklyn_Bridge_Manhattan.jpg",  # Brooklyn Bridge
            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Chichen_Itza_3.jpg/800px-Chichen_Itza_3.jpg",  # Chichen Itza
            "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Wheeldon_Gorge_lookout_at_Flinders_Ranges_National_Park.jpg/800px-Wheeldon_Gorge_lookout_at_Flinders_Ranges_National_Park.jpg",  # Mountain vista
            "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Palace_of_Versailles_June_2010.jpg/800px-Palace_of_Versailles_June_2010.jpg",  # Palace of Versailles
        ]
        
        # Alternative: Local tourist site images (if you prefer to download and use local files)
        self.local_tourist_sites = [
            "tourist_backgrounds/eiffel_tower.jpg",
            "tourist_backgrounds/big_ben.jpg", 
            "tourist_backgrounds/statue_liberty.jpg",
            "tourist_backgrounds/taj_mahal.jpg",
            "tourist_backgrounds/tower_bridge.jpg",
            "tourist_backgrounds/machu_picchu.jpg",
            "tourist_backgrounds/sydney_opera.jpg",
            "tourist_backgrounds/golden_gate.jpg",
            "tourist_backgrounds/neuschwanstein.jpg",
            "tourist_backgrounds/brooklyn_bridge.jpg"
        ]
        
    def download_image(self, url):
        """Download image from URL with better error handling"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            img = Image.open(BytesIO(response.content))
            return np.array(img)
        except requests.exceptions.RequestException as e:
            print(f"Network error downloading image from {url}: {e}")
            return None
        except Exception as e:
            print(f"Error processing image from {url}: {e}")
            return None
    
    def create_sample_backgrounds(self, output_dir="tourist_backgrounds"):
        """Create sample background images if downloads fail"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Create simple colored backgrounds as fallbacks
        backgrounds = []
        colors = [
            (135, 206, 235),  # Sky blue
            (34, 139, 34),    # Forest green  
            (255, 182, 193),  # Light pink
            (255, 165, 0),    # Orange
            (147, 112, 219),  # Medium purple
            (255, 20, 147),   # Deep pink
            (0, 191, 255),    # Deep sky blue
            (154, 205, 50),   # Yellow green
            (255, 69, 0),     # Red orange
            (75, 0, 130),     # Indigo
        ]
        
        for i, color in enumerate(colors):
            # Create a simple gradient background
            background = np.zeros((600, 800, 3), dtype=np.uint8)
            for y in range(600):
                factor = y / 600
                new_color = tuple(int(c * (0.5 + factor * 0.5)) for c in color)
                background[y, :] = new_color
            
            backgrounds.append(background)
            
            # Save as fallback
            cv2.imwrite(f"{output_dir}/fallback_bg_{i+1}.jpg", 
                       cv2.cvtColor(background, cv2.COLOR_RGB2BGR))
        
        return backgrounds
    
    def load_local_images(self, image_paths):
        """Load images from local paths"""
        images = []
        for path in image_paths:
            try:
                img = cv2.imread(path)
                if img is not None:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    images.append(img)
                    print(f"Successfully loaded: {path}")
                else:
                    print(f"Could not load image: {path}")
            except Exception as e:
                print(f"Error loading image {path}: {e}")
        return images
    
    def create_simple_person_mask(self, image):
        """Simple but effective method to create a person mask"""
        # For testing purposes, create a mask that includes the center portion of the image
        # This assumes people are roughly in the center of the photo
        height, width = image.shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)
        
        # Create a rectangle in the center area where people are likely to be
        margin_x = width // 6
        margin_y = height // 8
        
        # Fill the center area
        mask[margin_y:height-margin_y, margin_x:width-margin_x] = 255
        
        return mask
    
    def extract_people_improved_skin_detection(self, image):
        """Improved skin-based person detection"""
        # Convert to different color spaces
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        ycrcb = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
        
        # Multiple skin tone ranges in HSV
        skin_masks = []
        
        # HSV skin ranges (multiple ranges for different skin tones)
        hsv_ranges = [
            ([0, 20, 70], [20, 255, 255]),      # Light skin
            ([0, 30, 80], [25, 255, 255]),      # Medium skin  
            ([0, 40, 50], [15, 255, 255]),      # Another range
            ([160, 20, 70], [180, 255, 255]),   # Reddish skin tones
        ]
        
        for lower, upper in hsv_ranges:
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            skin_masks.append(mask)
        
        # YCrCb skin detection (often more reliable)
        ycrcb_mask = cv2.inRange(ycrcb, np.array([0, 133, 77]), np.array([255, 173, 127]))
        skin_masks.append(ycrcb_mask)
        
        # Combine all skin masks
        combined_skin = np.zeros_like(skin_masks[0])
        for mask in skin_masks:
            combined_skin = cv2.bitwise_or(combined_skin, mask)
        
        # Expand skin areas to include clothing and body
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
        expanded = cv2.dilate(combined_skin, kernel, iterations=2)
        
        # Clean up the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
        expanded = cv2.morphologyEx(expanded, cv2.MORPH_CLOSE, kernel)
        expanded = cv2.morphologyEx(expanded, cv2.MORPH_OPEN, kernel)
        
        return expanded
    
    def extract_people_grabcut_improved(self, image):
        """Improved GrabCut implementation"""
        height, width = image.shape[:2]
        mask = np.zeros((height, width), np.uint8)
        
        # Try face detection first
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
        
        if len(faces) > 0:
            # Use face detection to guide the rectangle
            face_areas = []
            for (x, y, w, h) in faces:
                face_areas.append((x, y, w, h, w*h))
            
            # Use largest face
            faces_sorted = sorted(face_areas, key=lambda x: x[4], reverse=True)
            x, y, w, h, _ = faces_sorted[0]
            
            # Expand around face to include body
            body_width = w * 2.5
            body_height = h * 4
            
            rect_x = max(0, int(x - body_width * 0.3))
            rect_y = max(0, int(y - h * 0.2))
            rect_w = min(width - rect_x, int(body_width))
            rect_h = min(height - rect_y, int(body_height))
            
            rectangle = (rect_x, rect_y, rect_w, rect_h)
        else:
            # Fallback: assume person is in center 60% of image
            margin_w, margin_h = width // 5, height // 6
            rectangle = (margin_w, margin_h, width - 2*margin_w, height - 2*margin_h)
        
        # Initialize models
        fgModel = np.zeros((1, 65), np.float64)
        bgModel = np.zeros((1, 65), np.float64)
        
        try:
            # Apply GrabCut
            cv2.grabCut(image, mask, rectangle, bgModel, fgModel, 5, cv2.GC_INIT_WITH_RECT)
            
            # Convert mask
            mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
            return mask2 * 255
            
        except Exception as e:
            print(f"GrabCut failed: {e}")
            # Fallback to rectangle mask
            mask_fallback = np.zeros((height, width), dtype=np.uint8)
            x, y, w, h = rectangle
            mask_fallback[y:y+h, x:x+w] = 255
            return mask_fallback
    
    def create_combined_mask(self, image, debug=False):
        """Create the best possible person mask by combining multiple methods"""
        print(f"    Creating mask using multiple methods...")
        
        # Method 1: Simple center-based mask (most reliable fallback)
        mask_simple = self.create_simple_person_mask(image)
        
        # Method 2: Skin-based detection
        mask_skin = self.extract_people_improved_skin_detection(image)
        
        # Method 3: GrabCut
        mask_grabcut = self.extract_people_grabcut_improved(image)
        
        # Combine masks intelligently
        # If skin detection found significant areas, use it as primary
        skin_coverage = np.sum(mask_skin > 0) / (image.shape[0] * image.shape[1])
        grabcut_coverage = np.sum(mask_grabcut > 0) / (image.shape[0] * image.shape[1])
        
        print(f"    Skin detection coverage: {skin_coverage:.1%}")
        print(f"    GrabCut coverage: {grabcut_coverage:.1%}")
        
        if skin_coverage > 0.05:  # If skin detection found reasonable amount
            # Use skin detection as base, intersect with GrabCut if it's reasonable
            if 0.1 < grabcut_coverage < 0.7:
                combined_mask = cv2.bitwise_and(mask_skin, mask_grabcut)
                if np.sum(combined_mask > 0) / (image.shape[0] * image.shape[1]) < 0.05:
                    # If intersection is too small, just use skin mask
                    combined_mask = mask_skin
            else:
                combined_mask = mask_skin
        elif 0.1 < grabcut_coverage < 0.7:  # GrabCut seems reasonable
            combined_mask = mask_grabcut
        else:
            # Fallback to simple center mask
            print(f"    Using fallback center mask")
            combined_mask = mask_simple
        
        # Final cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        
        final_coverage = np.sum(combined_mask > 0) / (image.shape[0] * image.shape[1])
        print(f"    Final mask coverage: {final_coverage:.1%}")
        
        return combined_mask
    
    def create_soft_mask(self, mask, blur_radius=3):
        """Create a soft-edged mask for better blending"""
        # Apply Gaussian blur to soften edges
        soft_mask = cv2.GaussianBlur(mask.astype(np.float32), (blur_radius*2+1, blur_radius*2+1), 0)
        
        # Normalize to 0-255 range
        if soft_mask.max() > 0:
            soft_mask = (soft_mask / soft_mask.max() * 255).astype(np.uint8)
        else:
            soft_mask = mask  # Return original if all zeros
        
        return soft_mask
    
    def blend_images(self, person_img, person_mask, background_img, position=(0, 0), scale=1.0):
        """Blend people with background with improved visibility"""
        # Resize person image and mask if needed
        if scale != 1.0:
            new_width = int(person_img.shape[1] * scale)
            new_height = int(person_img.shape[0] * scale)
            person_img = cv2.resize(person_img, (new_width, new_height))
            person_mask = cv2.resize(person_mask, (new_width, new_height))
        
        # Create soft mask for blending
        person_mask_soft = self.create_soft_mask(person_mask, blur_radius=2)
        
        # Ensure background is the right size
        bg_height, bg_width = background_img.shape[:2]
        person_height, person_width = person_img.shape[:2]
        
        # Calculate placement position
        x, y = position
        
        # Adjust bounds
        x = max(0, min(x, bg_width - person_width))
        y = max(0, min(y, bg_height - person_height))
        
        # Calculate actual dimensions that fit
        actual_width = min(person_width, bg_width - x)
        actual_height = min(person_height, bg_height - y)
        
        if actual_width <= 0 or actual_height <= 0:
            print("    Warning: Person doesn't fit in background, using original background")
            return background_img
        
        # Crop if needed
        person_img_cropped = person_img[:actual_height, :actual_width]
        person_mask_cropped = person_mask_soft[:actual_height, :actual_width]
        
        # Get background region
        roi = background_img[y:y+actual_height, x:x+actual_width].copy()
        
        # Normalize mask for blending (0 to 1)
        mask_norm = person_mask_cropped.astype(float) / 255.0
        if len(mask_norm.shape) == 2:
            mask_norm = np.stack([mask_norm] * 3, axis=2)
        
        # Blend: person where mask is 1, background where mask is 0
        blended_roi = person_img_cropped.astype(float) * mask_norm + roi.astype(float) * (1 - mask_norm)
        
        # Create result
        result = background_img.copy()
        result[y:y+actual_height, x:x+actual_width] = blended_roi.astype(np.uint8)
        
        # Print debug info
        mask_percentage = np.mean(mask_norm) * 100
        print(f"    Blended with {mask_percentage:.1f}% person visibility")
        
        return result
    
    def process_tourist_photos(self, source_images, output_dir="tourist_composites", use_local=False):
        """Main function to process tourist photos with improved debugging"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        results = []
        background_images = []
        
        # Try to get background images
        if use_local:
            print("Using local tourist site images...")
            for path in self.local_tourist_sites:
                if os.path.exists(path):
                    img = cv2.imread(path)
                    if img is not None:
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        background_images.append(img)
        else:
            print("Downloading tourist site images...")
            for i, site_url in enumerate(self.tourist_sites[:5]):  # Limit to 5 for testing
                print(f"  Downloading background {i+1}/5...")
                background = self.download_image(site_url)
                if background is not None:
                    background_images.append(background)
                else:
                    print(f"    Failed to download, skipping...")
        
        # If no backgrounds were loaded successfully, create sample ones
        if not background_images:
            print("No background images loaded successfully. Creating sample backgrounds...")
            background_images = self.create_sample_backgrounds()[:5]  # Limit for testing
        
        print(f"Successfully loaded {len(background_images)} background images")
        
        # Process each source image
        for i, source_img in enumerate(source_images):
            print(f"\nProcessing source image {i+1}/{len(source_images)}")
            print(f"  Source image size: {source_img.shape}")
            
            # Create person mask with debugging
            person_mask = self.create_combined_mask(source_img, debug=True)
            
            # Save mask for inspection
            mask_path = f"{output_dir}/debug_mask_source{i+1}.jpg"
            cv2.imwrite(mask_path, person_mask)
            print(f"  Mask saved to: {mask_path}")
            
            # Also save the original source for comparison
            source_path = f"{output_dir}/debug_source{i+1}.jpg"
            cv2.imwrite(source_path, cv2.cvtColor(source_img, cv2.COLOR_RGB2BGR))
            
            # Process with first few backgrounds
            for j, background in enumerate(background_images[:3]):  # Limit for testing
                print(f"\n  Creating composite {j+1}/{min(3, len(background_images))}")
                
                # Resize background to standard size
                background = cv2.resize(background, (800, 600))
                print(f"    Background size: {background.shape}")
                
                # Calculate better positioning and scaling
                bg_height, bg_width = background.shape[:2]
                person_height, person_width = source_img.shape[:2]
                
                # Scale to fit nicely in the scene (make people visible but not too large)
                max_person_width = bg_width * 0.4  # Max 40% of background width
                max_person_height = bg_height * 0.6  # Max 60% of background height
                
                scale_w = max_person_width / person_width
                scale_h = max_person_height / person_height
                scale = min(scale_w, scale_h, 1.0)  # Don't upscale
                
                print(f"    Scale factor: {scale:.2f}")
                
                # Position in lower center area
                new_width = int(person_width * scale)
                new_height = int(person_height * scale)
                
                x = (bg_width - new_width) // 2  # Center horizontally
                y = bg_height - new_height - 20   # 20 pixels from bottom
                
                print(f"    Positioning at: ({x}, {y}), size: {new_width}x{new_height}")
                
                # Create composite
                composite = self.blend_images(
                    source_img, person_mask, background,
                    position=(x, y), scale=scale
                )
                
                # Save result
                output_path = f"{output_dir}/composite_source{i+1}_bg{j+1}.jpg"
                cv2.imwrite(output_path, cv2.cvtColor(composite, cv2.COLOR_RGB2BGR))
                results.append(output_path)
                print(f"    Saved: {output_path}")
        
        return results
    
    def create_collage(self, image_paths, collage_path="tourist_collage.jpg"):
        """Create a collage of all composite images"""
        if not image_paths:
            return None
        
        # Load all images
        images = []
        for path in image_paths:
            img = cv2.imread(path)
            if img is not None:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (300, 225))  # Standardize size
                images.append(img)
        
        if not images:
            return None
            
        # Calculate grid dimensions
        n_images = len(images)
        cols = int(np.ceil(np.sqrt(n_images)))
        rows = int(np.ceil(n_images / cols))
        
        # Create collage
        collage = np.zeros((rows * 225, cols * 300, 3), dtype=np.uint8)
        
        for i, img in enumerate(images):
            row = i // cols
            col = i % cols
            collage[row*225:(row+1)*225, col*300:(col+1)*300] = img
        
        # Save collage
        cv2.imwrite(collage_path, cv2.cvtColor(collage, cv2.COLOR_RGB2BGR))
        return collage_path

def main():
    # Initialize the composer
    composer = TouristPhotoComposer()
    
    # Load your source images (replace with actual paths to your photos)
    source_image_paths = [
        "bill-shar2.jpg", 
        "bill-shar3.jpg", 
        "bill-shar4.jpg", 
        "bill-shar5.jpg", 
        "bill-shar6.jpg", 
        "bill-shar7.jpg" 
    ]
    
    print("Loading source images...")
    source_images = composer.load_local_images(source_image_paths)
    
    if not source_images:
        print("No source images found. Please check the file paths.")
        print("Make sure the images exist in the current directory or update the paths.")
        return
    
    print(f"Loaded {len(source_images)} source images")
    print("Creating tourist site composites...")
    
    # Process images
    results = composer.process_tourist_photos(source_images, use_local=False)
    
    print(f"\nCreated {len(results)} composite images!")
    print("Check the 'tourist_composites' folder for:")
    print("- debug_source*.jpg (original images)")
    print("- debug_mask*.jpg (person masks - white areas will be transferred)")
    print("- composite*.jpg (final composites)")
    
    # Create collage
    if results:
        collage_path = composer.create_collage(results)
        if collage_path:
            print(f"Collage saved to: {collage_path}")
    
    print("\nProcessing complete!")

if __name__ == "__main__":
    main()

