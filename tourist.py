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
        ]
        
        self.site_names = [
            "EiffelTower", "BigBen", "StatueLiberty", "TajMahal", "TowerBridge", 
            "MachuPicchu", "SydneyOpera", "SagradaFamilia", "GoldenGate", 
            "Neuschwanstein", "Colosseum", "BrooklynBridge"
        ]
        
    def download_image(self, url):
        """Download image from URL with better error handling"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            return np.array(img)
        except Exception as e:
            print(f"Error downloading from {url}: {e}")
            return None
    
    def load_local_images(self, image_paths):
        """Load images from local paths"""
        images = []
        valid_paths = []
        for path in image_paths:
            try:
                img = cv2.imread(path)
                if img is not None:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    images.append(img)
                    valid_paths.append(path)
                    print(f"Successfully loaded: {path} - Size: {img.shape}")
                else:
                    print(f"Could not load image: {path}")
            except Exception as e:
                print(f"Error loading image {path}: {e}")
        return images, valid_paths
    
    def create_advanced_person_mask(self, image):
        """Advanced person extraction using multiple techniques"""
        height, width = image.shape[:2]
        
        # Method 1: Advanced skin detection
        mask_skin = self.detect_skin_advanced(image)
        
        # Method 2: GrabCut with multiple initializations
        mask_grabcut = self.grabcut_multi_init(image)
        
        # Method 3: Edge-based segmentation
        mask_edges = self.edge_based_segmentation(image)
        
        # Method 4: Color-based clustering
        mask_cluster = self.color_clustering_mask(image)
        
        # Combine masks intelligently
        final_mask = self.combine_masks_smart([mask_skin, mask_grabcut, mask_edges, mask_cluster], image)
        
        return final_mask
    
    def detect_skin_advanced(self, image):
        """Advanced skin detection with multiple color spaces"""
        # Convert to different color spaces
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        ycrcb = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        
        # HSV skin detection (multiple ranges)
        hsv_lower1 = np.array([0, 20, 70])
        hsv_upper1 = np.array([20, 255, 255])
        hsv_lower2 = np.array([0, 30, 80]) 
        hsv_upper2 = np.array([25, 255, 255])
        
        hsv_mask1 = cv2.inRange(hsv, hsv_lower1, hsv_upper1)
        hsv_mask2 = cv2.inRange(hsv, hsv_lower2, hsv_upper2)
        hsv_mask = cv2.bitwise_or(hsv_mask1, hsv_mask2)
        
        # YCrCb skin detection (more robust)
        ycrcb_mask = cv2.inRange(ycrcb, np.array([0, 133, 77]), np.array([255, 173, 127]))
        
        # LAB skin detection
        lab_mask = cv2.inRange(lab, np.array([20, 15, 20]), np.array([255, 170, 120]))
        
        # Combine skin masks
        skin_mask = cv2.bitwise_or(cv2.bitwise_or(hsv_mask, ycrcb_mask), lab_mask)
        
        # Morphological operations to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
        
        # Dilate to include clothing near skin
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20))
        skin_mask = cv2.dilate(skin_mask, kernel, iterations=2)
        
        return skin_mask
    
    def grabcut_multi_init(self, image):
        """GrabCut with multiple initialization strategies"""
        height, width = image.shape[:2]
        
        # Try multiple rectangle initializations
        rectangles = []
        
        # Center rectangle
        margin_w, margin_h = width//5, height//6
        rectangles.append((margin_w, margin_h, width-2*margin_w, height-2*margin_h))
        
        # Face detection guided rectangle
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
        
        if len(faces) > 0:
            # Use largest face
            largest_face = max(faces, key=lambda x: x[2]*x[3])
            fx, fy, fw, fh = largest_face
            
            # Expand around face
            body_w, body_h = fw * 2.5, fh * 4
            rect_x = max(0, int(fx - body_w * 0.3))
            rect_y = max(0, int(fy - fh * 0.2))
            rect_w = min(width - rect_x, int(body_w))
            rect_h = min(height - rect_y, int(body_h))
            rectangles.append((rect_x, rect_y, rect_w, rect_h))
        
        # Try each rectangle and pick best result
        best_mask = None
        best_score = 0
        
        for rect in rectangles:
            try:
                mask = np.zeros((height, width), np.uint8)
                bgdModel = np.zeros((1, 65), np.float64)
                fgdModel = np.zeros((1, 65), np.float64)
                
                cv2.grabCut(image, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
                mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8') * 255
                
                # Score based on reasonable coverage
                coverage = np.sum(mask2 > 0) / (width * height)
                if 0.1 < coverage < 0.7:  # Reasonable person size
                    if coverage > best_score:
                        best_score = coverage
                        best_mask = mask2
                        
            except Exception as e:
                continue
        
        if best_mask is None:
            # Fallback
            mask = np.zeros((height, width), dtype=np.uint8)
            x, y, w, h = rectangles[0]
            mask[y:y+h, x:x+w] = 255
            return mask
            
        return best_mask
    
    def edge_based_segmentation(self, image):
        """Use edge detection to help identify person boundaries"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Multiple edge detection
        edges1 = cv2.Canny(gray, 30, 100)
        edges2 = cv2.Canny(gray, 50, 150)
        edges = cv2.bitwise_or(edges1, edges2)
        
        # Close gaps in edges
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # Find contours and filter by size/shape
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        mask = np.zeros(gray.shape, dtype=np.uint8)
        img_area = gray.shape[0] * gray.shape[1]
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if img_area * 0.02 < area < img_area * 0.6:  # Reasonable size
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = h / w if w > 0 else 0
                if 0.7 < aspect_ratio < 3.0:  # Person-like proportions
                    cv2.fillPoly(mask, [contour], 255)
        
        return mask
    
    def color_clustering_mask(self, image):
        """Use K-means clustering to separate foreground from background"""
        # Reshape image to be a list of pixels
        data = image.reshape((-1, 3))
        data = np.float32(data)
        
        # Apply K-means clustering
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(data, 4, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Convert back to image shape
        labels = labels.reshape(image.shape[:2])
        
        # Try to identify which clusters might be person vs background
        # This is heuristic - usually person clusters are in center area
        height, width = image.shape[:2]
        center_region = labels[height//4:3*height//4, width//4:3*width//4]
        
        # Find most common cluster in center
        unique, counts = np.unique(center_region, return_counts=True)
        person_cluster = unique[np.argmax(counts)]
        
        # Create mask
        mask = np.where(labels == person_cluster, 255, 0).astype(np.uint8)
        
        return mask
    
    def combine_masks_smart(self, masks, image):
        """Intelligently combine multiple masks"""
        height, width = image.shape[:2]
        img_area = height * width
        
        valid_masks = []
        mask_scores = []
        
        # Score each mask
        for mask in masks:
            coverage = np.sum(mask > 0) / img_area
            # Good masks have reasonable coverage and are roughly centered
            if 0.05 < coverage < 0.8:
                # Check if mask is somewhat centered (people usually are)
                center_y, center_x = height//2, width//2
                mask_moments = cv2.moments(mask)
                if mask_moments['m00'] > 0:
                    centroid_x = mask_moments['m10'] / mask_moments['m00']
                    centroid_y = mask_moments['m01'] / mask_moments['m00']
                    
                    # Distance from center (normalized)
                    dist_from_center = np.sqrt((centroid_x - center_x)**2 + (centroid_y - center_y)**2)
                    dist_from_center /= np.sqrt(center_x**2 + center_y**2)
                    
                    score = coverage * (1 - dist_from_center * 0.5)  # Prefer centered masks
                    valid_masks.append(mask)
                    mask_scores.append(score)
        
        if not valid_masks:
            # Fallback to center rectangle
            mask = np.zeros((height, width), dtype=np.uint8)
            margin_x, margin_y = width//4, height//6
            mask[margin_y:height-margin_y, margin_x:width-margin_x] = 255
            return mask
        
        # Use the two best masks and combine them
        sorted_indices = np.argsort(mask_scores)[::-1]
        
        if len(valid_masks) >= 2:
            # Combine top 2 masks
            best_mask = valid_masks[sorted_indices[0]]
            second_mask = valid_masks[sorted_indices[1]]
            combined = cv2.bitwise_or(best_mask, second_mask)
        else:
            combined = valid_masks[sorted_indices[0]]
        
        # Final cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel)
        combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel)
        
        return combined
    
    def create_clean_cutout(self, image, mask):
        """Create a clean cutout of the person with transparent background"""
        # Ensure mask is single channel
        if len(mask.shape) == 3:
            mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        
        # Create 4-channel image (RGBA)
        height, width = image.shape[:2]
        result = np.zeros((height, width, 4), dtype=np.uint8)
        
        # Copy RGB channels
        result[:,:,0:3] = image
        
        # Use mask as alpha channel
        result[:,:,3] = mask
        
        return result
    
    def blend_person_into_background(self, person_cutout, background, position=(0, 0), scale=1.0):
        """Blend person cutout into background with proper transparency"""
        # Resize person cutout if needed
        if scale != 1.0:
            new_width = int(person_cutout.shape[1] * scale)
            new_height = int(person_cutout.shape[0] * scale)
            person_cutout = cv2.resize(person_cutout, (new_width, new_height))
        
        bg_height, bg_width = background.shape[:2]
        person_height, person_width = person_cutout.shape[:2]
        
        # Adjust position to fit
        x, y = position
        x = max(0, min(x, bg_width - person_width))
        y = max(0, min(y, bg_height - person_height))
        
        # Calculate actual dimensions
        actual_width = min(person_width, bg_width - x)
        actual_height = min(person_height, bg_height - y)
        
        if actual_width <= 0 or actual_height <= 0:
            return background
        
        # Crop if necessary
        person_crop = person_cutout[:actual_height, :actual_width]
        
        # Extract alpha channel
        alpha = person_crop[:,:,3].astype(float) / 255.0
        alpha = np.stack([alpha] * 3, axis=2)  # Make 3-channel for RGB
        
        # Get background region
        bg_region = background[y:y+actual_height, x:x+actual_width].astype(float)
        person_rgb = person_crop[:,:,0:3].astype(float)
        
        # Blend
        blended = person_rgb * alpha + bg_region * (1 - alpha)
        
        # Create result
        result = background.copy().astype(float)
        result[y:y+actual_height, x:x+actual_width] = blended
        
        return result.astype(np.uint8)
    
    def process_individual_tourist_photos(self, source_images, source_paths, output_dir="individual_tourist_photos"):
        """Create individual photos for each person at each tourist site"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Load background images
        print("Loading tourist site backgrounds...")
        background_images = []
        site_names = []
        
        for i, site_url in enumerate(self.tourist_sites):
            print(f"  Loading site {i+1}/{len(self.tourist_sites)}: {self.site_names[i]}")
            background = self.download_image(site_url)
            if background is not None:
                # Resize to standard size
                background = cv2.resize(background, (1200, 800))
                background_images.append(background)
                site_names.append(self.site_names[i])
            else:
                print(f"    Failed to load {self.site_names[i]}")
        
        if not background_images:
            print("No background images loaded successfully!")
            return []
        
        print(f"Successfully loaded {len(background_images)} tourist sites")
        
        results = []
        
        # Process each source image
        for source_idx, (source_img, source_path) in enumerate(zip(source_images, source_paths)):
            print(f"\nProcessing {source_path}...")
            
            # Extract person mask
            print("  Creating person mask...")
            person_mask = self.create_advanced_person_mask(source_img)
            
            # Save debug mask
            mask_debug_path = f"{output_dir}/debug_mask_{source_idx+1}.jpg"
            cv2.imwrite(mask_debug_path, person_mask)
            print(f"  Debug mask saved: {mask_debug_path}")
            
            # Check mask quality
            coverage = np.sum(person_mask > 0) / (person_mask.shape[0] * person_mask.shape[1])
            print(f"  Mask coverage: {coverage:.1%}")
            
            if coverage < 0.05:
                print(f"  Warning: Very small mask detected, results may be poor")
            elif coverage > 0.8:
                print(f"  Warning: Very large mask detected, may include background")
            
            # Create clean person cutout
            person_cutout = self.create_clean_cutout(source_img, person_mask)
            
            # Extract base filename
            base_name = os.path.splitext(os.path.basename(source_path))[0]
            
            # Place person at each tourist site
            for bg_idx, (background, site_name) in enumerate(zip(background_images, site_names)):
                print(f"    Creating photo at {site_name}...")
                
                # Calculate positioning and scale
                bg_height, bg_width = background.shape[:2]
                person_height, person_width = person_cutout.shape[:2]
                
                # Scale person to fit nicely (max 30% of background width)
                max_person_width = bg_width * 0.3
                max_person_height = bg_height * 0.5
                
                scale_w = max_person_width / person_width
                scale_h = max_person_height / person_height
                scale = min(scale_w, scale_h, 1.0)  # Don't upscale
                
                # Position in lower center area
                new_width = int(person_width * scale)
                new_height = int(person_height * scale)
                
                x = (bg_width - new_width) // 2  # Center horizontally
                y = bg_height - new_height - 50   # 50 pixels from bottom
                
                # Create the composite
                result_img = self.blend_person_into_background(
                    person_cutout, background, 
                    position=(x, y), scale=scale
                )
                
                # Save individual photo
                output_filename = f"{base_name}_at_{site_name}.jpg"
                output_path = os.path.join(output_dir, output_filename)
                
                cv2.imwrite(output_path, cv2.cvtColor(result_img, cv2.COLOR_RGB2BGR))
                results.append(output_path)
                print(f"      Saved: {output_filename}")
        
        return results

def main():
    # Initialize the composer
    composer = TouristPhotoComposer()
    
    # Load your source images
    source_image_paths = [
        "bill-shar2.png", 
        "bill-shar3.png", 
        "bill-shar4.png", 
        "bill-shar5.png", 
        "bill-shar6.png", 
        "bill-shar7.png" 
    ]
    
    print("Loading source images...")
    source_images, valid_paths = composer.load_local_images(source_image_paths)
    
    if not source_images:
        print("\n❌ No source images found!")
        print("Please make sure the following files exist in your current directory:")
        for path in source_image_paths:
            print(f"  - {path}")
        return
    
    print(f"\n✅ Loaded {len(source_images)} source images")
    
    print("\n🏛️ Creating individual tourist photos...")
    print("This will create separate photos of each person at each tourist site")
    
    # Create individual photos
    results = composer.process_individual_tourist_photos(source_images, valid_paths)
    
    print(f"\n🎉 Created {len(results)} individual tourist photos!")
    print(f"\n📁 Check the 'individual_tourist_photos' folder for:")
    print("  - debug_mask_*.jpg (shows what areas were detected as people)")
    print("  - *_at_*.jpg (individual photos at each tourist site)")
    
    if len(results) == 0:
        print("\n⚠️  No photos were created. Check the debug masks to see if person detection is working.")
        print("If masks are poor, you may need photos with:")
        print("  - Better lighting and contrast")
        print("  - People clearly separated from backgrounds")
        print("  - Less cluttered backgrounds")

if __name__ == "__main__":
    main()



