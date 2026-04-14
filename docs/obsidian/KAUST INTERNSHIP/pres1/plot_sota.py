import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Simple scatter: Paper impact (x) vs Hardware suitability (y)
fig, ax = plt.subplots(figsize=(8, 6))

papers = {
    'SkyCell': (9, 9, '#27ae60', 'circle'),
    'SkyRAN': (8, 8, '#27ae60', 'circle'),
    'Flying Rebots': (5, 5, '#f39c12', 'triangle'),
    'Jetson Nano\nOAI': (2, 3, '#e74c3c', 'square'),
    '5G Edge\nVision': (1, 2, '#e74c3c', 'square'),
}

for name, (x, y, color, marker) in papers.items():
    if marker == 'circle':
        ax.scatter(x, y, s=300, c=color, marker='o', edgecolors='black', linewidth=1.5, zorder=3)
    elif marker == 'triangle':
        ax.scatter(x, y, s=300, c=color, marker='^', edgecolors='black', linewidth=1.5, zorder=3)
    else:
        ax.scatter(x, y, s=300, c=color, marker='s', edgecolors='black', linewidth=1.5, zorder=3)
    ax.annotate(name, (x, y), xytext=(8, y+0.5), fontsize=10, ha='right')

ax.set_xlabel('Hardware Suitability for UAV-BS (1-10)', fontsize=12)
ax.set_ylabel('Research Impact / Relevance (1-10)', fontsize=12)
ax.set_title('Literature Map: UAV-BS Research', fontsize=14, fontweight='bold')
ax.set_xlim(0, 10.5)
ax.set_ylim(0, 10.5)
ax.grid(True, alpha=0.3)

# Quadrant lines
ax.axhline(y=5, color='gray', linestyle='--', alpha=0.5)
ax.axvline(x=5, color='gray', linestyle='--', alpha=0.5)

# Labels
ax.text(7.5, 8.5, 'HIGH: Proven UAV-BS\n(NUC + USRP B210)', fontsize=9, ha='center', color='#27ae60', style='italic')
ax.text(2.5, 2, 'LOW: Unsuitable\nfor aerial BS', fontsize=9, ha='center', color='#e74c3c', style='italic')

plt.tight_layout()
plt.savefig('sota_papers_map.png', dpi=150, bbox_inches='tight')
plt.close()
print("Created: sota_papers_map.png")
