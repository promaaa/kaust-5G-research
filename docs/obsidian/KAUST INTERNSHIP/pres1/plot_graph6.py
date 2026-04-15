import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import matplotlib.ticker as ticker

# Data
devices = [
    "Jetson Orin Nano\n(8GB)", 
    "Raspberry Pi 5", 
    "Intel N100", 
    "Intel i7-1185G7", 
    "Intel i7-1260P", 
    "AMD Ryzen 7\n7840HS"
]
single_scores = [700, 800, 1200, 1750, 2200, 2600]
multi_scores = [3000, 2700, 3200, 6000, 9500, 13500]

colors = [
    "#76B900", # Jetson
    "#C51A4A", # Raspberry Pi
    "#0071C5", # Intel
    "#0071C5", # Intel
    "#0071C5", # Intel
    "#ED1C24"  # AMD
]

x = np.arange(len(devices))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 7))

rects1 = ax.bar(x - width/2, single_scores, width, label='Single-Core', color=colors, alpha=0.5, edgecolor='black', linewidth=1.2, zorder=3)
rects2 = ax.bar(x + width/2, multi_scores, width, label='Multi-Core', color=colors, edgecolor='black', linewidth=1.2, zorder=3)

ax.set_ylabel('Benchmark Score', fontsize=12, fontweight='bold', labelpad=10)
ax.set_title('CPU Performance Comparison for OAI UABS Deployment', pad=20, fontsize=16, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(devices, fontsize=11, fontweight='500')

ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

core_legend_elements = [
    Patch(facecolor='gray', alpha=0.5, edgecolor='black', linewidth=1.2, label='Single-Core'),
    Patch(facecolor='gray', alpha=1.0, edgecolor='black', linewidth=1.2, label='Multi-Core')
]
core_legend = ax.legend(handles=core_legend_elements, loc='upper left', fontsize=11, framealpha=0.9)
ax.add_artist(core_legend)

arch_legend_elements = [
    Patch(facecolor='#76B900', edgecolor='black', linewidth=1.2, label='NVIDIA (ARM)'),
    Patch(facecolor='#C51A4A', edgecolor='black', linewidth=1.2, label='Raspberry Pi (ARM)'),
    Patch(facecolor='#0071C5', edgecolor='black', linewidth=1.2, label='Intel (x86)'),
    Patch(facecolor='#ED1C24', edgecolor='black', linewidth=1.2, label='AMD (x86)')
]
ax.legend(handles=arch_legend_elements, loc='upper left', bbox_to_anchor=(0.18, 1), fontsize=11, framealpha=0.9, title="Architecture")

ax.grid(axis='y', linestyle='--', alpha=0.7, zorder=0)
ax.set_ylim(0, 15500)

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{int(height):,}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, 
                    rotation=0, fontweight='bold', color='#333333')

autolabel(rects1)
autolabel(rects2)

fig.tight_layout()

output_path = '/Users/promaa/Documents/kaust-5G-research/docs/obsidian/KAUST INTERNSHIP/pres1/graph6_benchmark_comparison.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Graph successfully saved to {output_path}")