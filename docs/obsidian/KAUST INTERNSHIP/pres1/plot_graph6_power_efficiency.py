import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

devices = [
    "Jetson Orin Nano", 
    "Raspberry Pi 5", 
    "Intel N100", 
    "Intel i7-1185G7", 
    "Intel i7-1260P", 
    "AMD Ryzen 7 7840HS"
]

tdp = [15, 8, 6, 28, 28, 38]
single_scores = [700, 800, 1200, 1750, 2200, 2600]
multi_scores = [3000, 2700, 3200, 6000, 9500, 13500]

single_eff = [s / t for s, t in zip(single_scores, tdp)]
multi_eff = [m / t for m, t in zip(multi_scores, tdp)]

colors = ["#76B900", "#C51A4A", "#0071C5", "#0071C5", "#0071C5", "#ED1C24"]

x = np.arange(len(devices))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 7))

rects1 = ax.bar(x - width/2, single_eff, width, label='Single-Core', color=colors, alpha=0.5, edgecolor='black', linewidth=1.2)
rects2 = ax.bar(x + width/2, multi_eff, width, label='Multi-Core', color=colors, edgecolor='black', linewidth=1.2)

ax.set_ylabel('Performance / Watt (Score per Watt)', fontsize=12, fontweight='bold')
ax.set_title('CPU Power Efficiency Comparison for UAV Base Station Deployment', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(devices, fontsize=11)

for rect, val in zip(rects1, single_eff):
    ax.annotate(f'{val:.0f}', xy=(rect.get_x() + rect.get_width()/2, val), xytext=(0, 3), textcoords='offset points', ha='center', fontsize=9)
for rect, val in zip(rects2, multi_eff):
    ax.annotate(f'{val:.0f}', xy=(rect.get_x() + rect.get_width()/2, val), xytext=(0, 3), textcoords='offset points', ha='center', fontsize=9)

arch_elements = [
    Patch(facecolor='#76B900', edgecolor='black', label='NVIDIA ARM'),
    Patch(facecolor='#C51A4A', edgecolor='black', label='Raspberry Pi ARM'),
    Patch(facecolor='#0071C5', edgecolor='black', label='Intel x86'),
    Patch(facecolor='#ED1C24', edgecolor='black', label='AMD x86')
]
ax.legend(handles=arch_elements, loc='upper right', fontsize=10, title='Architecture')

ax.grid(axis='y', linestyle='--', alpha=0.7)
ax.set_ylim(0, 550)

fig.tight_layout()
plt.savefig('/Users/promaa/Documents/kaust-5G-research/docs/obsidian/KAUST INTERNSHIP/pres1/graph6_power_efficiency.png', dpi=300)
print("Saved: graph6_power_efficiency.png")