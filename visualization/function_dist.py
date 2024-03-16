import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Initialize random values for functions f1 to f8
f_values = {'f1': np.random.randint(100), 'f2': np.random.randint(100), 'f3': np.random.randint(100),
            'f4': np.random.randint(50), 'f5': np.random.randint(50), 'f6': np.random.randint(30),
            'f7': np.random.randint(30), 'f8': np.random.randint(30)}
# Convert dictionary to lists for plotting
functions, values = zip(*f_values.items())

# Setting the seaborn style for better aesthetics
sns.set(style="whitegrid")

# Creating the horizontal bar chart with each bar a different color
plt.figure(figsize=(10, 6))
palette = sns.color_palette("hsv", len(functions))  # Generate a color palette with a distinct color for each bar
sns.barplot(x=list(values), y=list(functions), palette=palette)  # Swap x and y values to make the chart horizontal
plt.title('Usage distribution of functions of same contract')
plt.xlabel('Random Values')  # Swap the labels as well
plt.ylabel('Functions')
plt.show()
