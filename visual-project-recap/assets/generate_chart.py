import matplotlib.pyplot as plt
import numpy as np

# Set dark background style parameters to match the slate theme
plt.rcParams['figure.facecolor'] = '#0b0f19'
plt.rcParams['axes.facecolor'] = '#0f172a'
plt.rcParams['text.color'] = '#f8fafc'
plt.rcParams['axes.labelcolor'] = '#94a3b8'
plt.rcParams['xtick.color'] = '#94a3b8'
plt.rcParams['ytick.color'] = '#94a3b8'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Inter', 'DejaVu Sans', 'Arial']

# Data
categories = [
    'Transport 5G Quectel\n(Double liaison sans fil)',
    'Liaison nrUE isolée\n(Test 5G USRP à USRP)',
    'Tunnel GRE sur Wi-Fi\n(Liaison F1 sans fil)',
    'Séparation Ethernet\n(Câble Gigabit - bridé)',
    '5G monolithique\n(Référence sur PC unique)'
]
throughput = [3.1, 8.6, 12.0, 23.0, 150.0]
colors = ['#f43f5e', '#f59e0b', '#eab308', '#3b82f6', '#10b981']

fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

# Create horizontal bar chart
bars = ax.barh(categories, throughput, color=colors, height=0.6, edgecolor='none')

# Add titles and labels
ax.set_title('Comparaison du débit selon le mode de déploiement', fontsize=14, fontweight='bold', pad=20, color='#f8fafc')
ax.set_xlabel('Débit de l\'utilisateur (Mbps)', fontsize=11, labelpad=10)

# Configure grids
ax.xaxis.grid(True, linestyle='--', alpha=0.15, color='#e2e8f0')
ax.set_axisbelow(True)

# Remove spines
for spine in ['top', 'right', 'left', 'bottom']:
    ax.spines[spine].set_visible(False)

# Add values at the end of each bar
for bar in bars:
    width = bar.get_width()
    ax.text(width + 3, bar.get_y() + bar.get_height()/2, f'{width:.1f} Mbps', 
            va='center', ha='left', fontsize=10, fontweight='bold', color='#f8fafc')

# Set x-limit with some padding
ax.set_xlim(0, 175)

plt.tight_layout()

# Save image
plt.savefig('performance_comparison.png', bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
print("Successfully generated performance_comparison.png in French")
