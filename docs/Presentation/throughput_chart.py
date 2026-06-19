#!/usr/bin/env python3
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Data
configs = [
    'Monolithic\nOAI reference',
    'Ethernet CU/DU\nwith SIB8',
    'Wi-Fi CU/DU\nwith SIB8',
    'Quectel 5G F1\nbackhaul'
]
throughputs = [150, 21, 12, 50]  # Middle value for Ethernet range
labels = ['150 Mbps', '19-23 Mbps', '12 Mbps', '50 Mbps']

# Colors
colors = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c']

fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.bar(configs, throughputs, color=colors, edgecolor='white', linewidth=1.5)

# Add value labels on bars
for bar, label in zip(bars, labels):
    height = bar.get_height()
    ax.annotate(label,
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 5),
                textcoords="offset points",
                ha='center', va='bottom',
                fontsize=12, fontweight='bold')

ax.set_ylabel('Throughput (Mbps)', fontsize=12)
ax.set_title('Observed Throughput by Configuration', fontsize=14, fontweight='bold')
ax.set_ylim(0, 180)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.tick_params(axis='both', labelsize=10)

plt.tight_layout()
plt.savefig('throughput_chart.png', dpi=150, bbox_inches='tight')
print('Saved: throughput_chart.png')
