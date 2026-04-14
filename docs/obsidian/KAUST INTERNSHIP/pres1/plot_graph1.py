import matplotlib.pyplot as plt
import numpy as np

# Exact data and style from generate_graphs.py (Graph 1) - Only Translated
labels = ['Theoretical\n(USB 3.2)', 'x86 Mini-PC', 'Jetson Orin\n(Measured)', '5G NR\nMinimum']
values = [10, 7, 3, 4.5]
colors = ['#4CAF50', '#2196F3', '#F44336', '#9C27B0']

fig, ax = plt.subplots(figsize=(8, 4))

ax.bar(labels, values, color=colors, width=0.5, edgecolor='black', linewidth=0.5)

for i, v in enumerate(values):
    ax.text(i, v + 0.3, f'{v} Gbps', ha='center', fontsize=10, fontweight='bold')

ax.set_ylabel('Bandwidth (Gbps)')
ax.set_title('USB 3.2 Bandwidth Comparison')
ax.set_ylim(0, 12)
ax.axhline(y=4.5, color='red', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('graph1_bandwidth_comparison.png', facecolor='white')
plt.close()
print("Created: graph1_bandwidth_comparison.png")
