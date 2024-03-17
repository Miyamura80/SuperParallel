import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns

# Setting the seaborn style for better aesthetics
sns.set(style="white")

# Creating a 26x26x26 grid matrix with alphabet annotations
grid_size = 26
grid_matrix = np.zeros((grid_size, grid_size, grid_size))
alphabet = [chr(i) for i in range(97, 123)]  # Generating a list of alphabets

# Generating random red spots in the lower part of the 3D matrix
for i in range(grid_size):
    for j in range(grid_size):
        for k in range(grid_size):
            if i >= j and j >= k:  # Ensuring lower part of the matrix
                if np.random.rand() > 0.8:  # Random condition to place a red spot
                    grid_matrix[i, j, k] = 1  # Marking red spots

# Creating a color map where 1 corresponds to red and 0 to black
cmap = sns.color_palette(["black", "red"])
sns.set_palette(cmap)

# Plotting the 3D grid matrix
fig = plt.figure(figsize=(12, 12))
ax = fig.add_subplot(111, projection='3d')

# Generating coordinates for red spots
x, y, z = np.indices((grid_size, grid_size, grid_size))
x, y, z = x[grid_matrix == 1], y[grid_matrix == 1], z[grid_matrix == 1]

# Plotting red spots
ax.scatter(x, y, z, c='red', marker='o')

# Setting labels and title
ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')
plt.title('3D Bloom Filter for Address Overlap for Contract 3')

plt.show()
