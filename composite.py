
import os
import glob
from PIL import Image

# Get a list of all bill*.jpg files
image_paths = sorted(glob.glob('ezgif*.jpg'))
images = [Image.open(p) for p in image_paths]

if not images:
    print("No images found.")
    exit()

# Assuming all images are the same size, get dimensions from the first image
img_width, img_height = images[0].size

# Create a 4x4 grid
grid_size = 4
composite_width = grid_size * img_width
composite_height = grid_size * img_height

# Create a new blank image
composite_image = Image.new('RGB', (composite_width, composite_height))

# Paste images into the grid
for index, img in enumerate(images):
    if index >= grid_size * grid_size:
        break
    row = index // grid_size
    col = index % grid_size
    x_offset = col * img_width
    y_offset = row * img_height
    composite_image.paste(img, (x_offset, y_offset))

# Save the composite image
composite_image.save('bill_composite.jpg')
print("Composite image saved as bill_composite.jpg")
