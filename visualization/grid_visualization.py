import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Setting the seaborn style for better aesthetics
sns.set(style="white")

# Creating a 26x26 grid matrix with alphabet annotations
grid_size = 26
grid_matrix = np.zeros((grid_size, grid_size))
alphabet = [chr(i) for i in range(97, 123)]  # Generating a list of alphabets

# Generating random red spots in the lower triangular part of the matrix
for i in range(grid_size):
    for j in range(i+1):
        if np.random.rand() > 0.9:  # Random condition to place a red spot
            grid_matrix[i, j] = 1  # Marking red spots

# Creating a color map where 1 corresponds to red and 0 to black
cmap = sns.color_palette(["black", "red"])
sns.set_palette(cmap)

# Plotting the grid matrix with alphabet annotations
plt.figure(figsize=(12, 12))
sns.heatmap(grid_matrix, cmap=cmap, cbar=False, linecolor='black', linewidths=0.5, xticklabels=alphabet, yticklabels=alphabet)
plt.title('Bloom Filter for Address Overlap for Contract 3')
plt.show()
