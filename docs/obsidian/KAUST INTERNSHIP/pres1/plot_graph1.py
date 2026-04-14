import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Graph 1: USB DMA Bandwidth Comparison (simple bar chart)
fig, ax = plt.subplots(figsize=(8, 5))

labels = ['Jetson Nano\n(measured)', '5G NR 20MHz\n(required)', '5G NR 100MHz\n(required)']
values = [3.0, 4.8, 24.0]
colors = ['#e74c3c', '#27ae60', '#27ae60']

bars = ax.bar(labels, values, color=colors, width=0.6, edgecolor='black', linewidth=1.2)

ax.set_ylabel('Bandwidth (Gbps)', fontsize=12)
ax.set_title('USB 3.0 DMA Bandwidth: Jetson Nano vs 5G Requirements', fontsize=13, fontweight='bold')
ax.set_ylim(0, 28)

for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{val:.1f} Gbps',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('graph1_bandwidth_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("Graph 1 saved: graph1_bandwidth_comparison.png")
