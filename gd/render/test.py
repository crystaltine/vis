import numpy as np

# Define the mix_colors function
def mix_colors(color1, color2):
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    # Example mix: average the colors
    return np.array([(r1 + r2) // 2, (g1 + g2) // 2, (b1 + b2) // 2])

# Create two example 3D arrays (2x2 images with 3 color channels)
array1 = np.array([[[255, 0, 0], [0, 255, 0]],
                   [[0, 0, 255], [255, 255, 0]]])

array2 = np.array([[[0, 255, 255], [255, 0, 255]],
                   [[255, 255, 255], [0, 0, 0]]])

# Apply the mix_colors function along the last axis
def func(x):
    print(x)
    return mix_colors(x[:3], x[3:])

result = np.apply_along_axis(func, 2, np.dstack((array1, array2)))

print("Resulting array:")
print(result)