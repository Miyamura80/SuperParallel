

tps_per_chain = {
    "Ethereum": 12,
    "Solana": 2525,
    "NeonEVM": 2000,
    "Monad": 10000,
    "Sei": 5000,
    "SuperParallel": 100000,
}

import matplotlib.pyplot as plt
import seaborn as sns

# Setting the seaborn style for better aesthetics
sns.set(style="whitegrid")

# Extracting chain names and their TPS
chains = list(tps_per_chain.keys())
tps_values = list(tps_per_chain.values())

# Creating the bar chart in log scale with seaborn
plt.figure(figsize=(10, 6))
sns.barplot(x=chains, y=tps_values, palette='viridis', log=True)  # Using a color palette for different colors

plt.xlabel('Blockchain')
plt.ylabel('Transactions Per Second (TPS) - Log Scale')
plt.title('Blockchain TPS Comparison (Log Scale)')
plt.xticks(rotation=45)
plt.tight_layout()

# Display the chart
plt.show()
