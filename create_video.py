
import cv2
import glob
import os

# Get a sorted list of image files
image_files = sorted(glob.glob('ezgif-frame-*.jpg'))

if not image_files:
    print("No image files found.")
    exit()

# Read the first image to get the dimensions
frame = cv2.imread(image_files[0])
height, width, layers = frame.shape

# Define the codec and create VideoWriter object
# Using 'mp4v' codec for .mp4 file
fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
video = cv2.VideoWriter('output.mp4', fourcc, 10, (width, height))

# Write each image to the video file
for image_file in image_files:
    frame = cv2.imread(image_file)
    video.write(frame)

# Release the video writer
video.release()

print("Video 'output.mp4' created successfully.")
