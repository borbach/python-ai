from PIL import Image
import numpy as np

def composite_hologram(image_paths, output_path):
    # Load all images
    images = [Image.open(path).convert("RGB") for path in image_paths]
    
    # Ensure all images have the same size
    if not all(img.size == images[0].size for img in images):
        raise ValueError("All images must have the same dimensions")
    
    # Convert images to numpy arrays
    image_arrays = [np.array(img) for img in images]
    
    # Initialize a composite image array
    composite_array = np.zeros_like(image_arrays[0], dtype=np.float64)
    
    # Combine images using a simple averaging approach (you can customize this)
    for arr in image_arrays:
        composite_array += arr
    
    # Normalize the composite array to ensure it is within valid RGB range
    composite_array /= len(image_arrays)
    composite_array = np.clip(composite_array, 0, 255).astype(np.uint8)
    
    # Convert the composite array back to a PIL image
    composite_image = Image.fromarray(composite_array)
    
    # Save the composite image
    composite_image.save(output_path)
    print(f"Composite hologram saved to {output_path}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate a composite hologram from multiple JPEG files.")
    parser.add_argument("input_files", nargs="+", help="Paths to input JPG files")
    parser.add_argument("output_file", help="Path to output the composite hologram file")
    
    args = parser.parse_args()
    
    try:
        composite_hologram(args.input_files, args.output_file)
    except Exception as e:
        print(f"Error: {e}")

