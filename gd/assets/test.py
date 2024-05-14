from PIL import Image

# Load the image
image = Image.open('gd/assets/play_button.jpeg')

# Resize the image to a smaller size for better ASCII representation
width, height = image.size
aspect_ratio = height / width
new_width = 100
new_height = int(aspect_ratio * new_width * 0.55)  # Adjust aspect ratio
image = image.resize((new_width, new_height))

# Convert the image to grayscale
image = image.convert("L")

# Define the ASCII characters to represent different shades of gray
ascii_chars = "@%#*+=-:. "

# Convert each pixel to an ASCII character based on its brightness
ascii_image = ""
pixels = image.getdata()
for pixel_value in pixels:
    ascii_image += ascii_chars[pixel_value // 32]

# Split the ASCII image into lines
ascii_image_lines = [ascii_image[i:i+new_width] for i in range(0, len(ascii_image), new_width)]

# Print the ASCII image to the terminal
for line in ascii_image_lines:
    print(line)