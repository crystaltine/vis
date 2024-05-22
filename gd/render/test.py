from PIL import Image
import numpy as np

filepath = "test.png"
im = Image.open(filepath)
pixels = np.array(im, dtype=np.uint8)

print(pixels)