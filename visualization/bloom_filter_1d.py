import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Setting the seaborn style for better aesthetics
sns.set(style="white")

# Creating a 26 element array with alphabet annotations
array_size = 26
array = np.zeros(array_size)
alphabet = [chr(i) for i in range(97, 123)]  # Generating a list of alphabets

# Generating random red spots across the array
for i in range(array_size):
    if np.random.rand() > 0.8:  # Random condition to place a red spot
        array[i] = 1  # Marking red spots

# Creating a color map where 1 corresponds to red and 0 to black
cmap = sns.color_palette(["black", "red"])
sns.set_palette(cmap)

# Plotting the array with alphabet annotations
plt.figure(figsize=(12, 2))
sns.heatmap([array], cmap=cmap, cbar=False, linecolor='black', linewidths=0.5, xticklabels=alphabet, yticklabels=False)
plt.title('Bloom Filter for Address Overlap for Contract 1')
plt.show()
