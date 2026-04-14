import matplotlib.pyplot as plt
import numpy as np

# Graph 5: Hardware Comparison (simple table-style bar chart)
fig, ax = plt.subplots(figsize=(9, 5))

categories = ['AVX-512\nSupport', 'USB Power\nStability', 'DMA Bandwidth\n(Gbps)', 'Flight\nTested', 'Form Factor\n(portability)']
jetson_scores = [0, 1, 3, 0, 5]
nuc_scores = [5, 5, 24, 5, 3]

x = np.arange(len(categories))
width = 0.35

bars1 = ax.bar(x - width/2, jetson_scores, width, label='Jetson Nano', color='#e74c3c', edgecolor='black')
bars2 = ax.bar(x + width/2, nuc_scores, width, label='Intel NUC', color='#27ae60', edgecolor='black')

ax.set_ylabel('Score (0-5)', fontsize=12)
ax.set_title('Hardware Comparison: Jetson Nano vs Intel NUC', fontsize=13, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.legend()
ax.set_ylim(0, 6)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', alpha=0.3)

for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig('graph5_hardware_comparison_matrix.png', dpi=150, bbox_inches='tight')
plt.close()
print("Graph 5 saved: graph5_hardware_comparison_matrix.png")
