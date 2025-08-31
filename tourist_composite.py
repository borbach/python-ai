import requests
import os
from PIL import Image
from rembg import remove
import glob
import sys
import io

# --- Configuration ---
INPUT_IMAGE_PATH = sorted(glob.glob('ezgif-frame-*.jpg'))[0]
OUTPUT_DIR = "tourist_images"
CITIES = {
    "new_york": "Times Square",
    "london": "Tower Bridge",
    "paris": "Eiffel Tower",
    "jerusalem": "Western Wall",
    "prague": "Charles Bridge",
    "istanbul": "Hagia Sophia",
    "athens": "Acropolis"
}

# --- Get image URLs from command line arguments ---
image_urls = sys.argv[1:]
city_keys = list(CITIES.keys())

if len(image_urls) == 1:
    city_keys = ["paris"]
elif len(image_urls) != len(CITIES) and len(image_urls) != 0:
    print(f"Error: Please provide either 1 (for Paris) or {len(CITIES)} image URLs as command-line arguments.")
    sys.exit(1)
elif len(image_urls) == 0:
    print("No image URLs provided. Exiting.")
    sys.exit(0)


# --- Create output directory ---
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# --- 1. Remove background from the input image ---
print("Removing background from input image...")
with open(INPUT_IMAGE_PATH, 'rb') as f_in:
    input_image_data = f_in.read()
    output_image_data = remove(input_image_data)

foreground = Image.open(io.BytesIO(output_image_data)).convert("RGBA")
print("Background removal complete.")

# --- 2. Process each city ---
for i, city in enumerate(city_keys):
    landmark = CITIES[city]
    image_url = image_urls[i]
    print(f"Processing {city}...")

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/53.7.3'}
        response = requests.get(image_url, stream=True, timeout=15, headers=headers)
        response.raise_for_status()
        background = Image.open(response.raw).convert("RGBA")
        print(f"Successfully downloaded background for {landmark}.")

        # --- 4. Composite the images ---
        bg_width, bg_height = background.size
        fg_width, fg_height = foreground.size

        ratio = (bg_height / 3) / fg_height
        new_fg_width = int(fg_width * ratio)
        new_fg_height = int(fg_height * ratio)
        
        resized_foreground = foreground.resize((new_fg_width, new_fg_height), Image.LANCZOS)

        paste_x = (bg_width - new_fg_width) // 2
        paste_y = bg_height - new_fg_height

        composite = Image.new("RGBA", background.size)
        composite.paste(background, (0, 0))
        composite.paste(resized_foreground, (paste_x, paste_y), resized_foreground)

        # --- 5. Save the result ---
        output_path = os.path.join(OUTPUT_DIR, f"{city}_{landmark.replace(' ', '_')}.png")
        composite.save(output_path)
        print(f"Saved composite image to {output_path}")

    except requests.exceptions.RequestException as e:
        print(f"Could not download background for {landmark}: {e}")
    except Exception as e:
        print(f"An error occurred while processing {city}: {e}")

print("\nAll cities processed.")