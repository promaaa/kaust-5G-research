#!/usr/bin/env python3
"""Graphiques de comparaison matériel - Français"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'figure.dpi': 150,
    'savefig.dpi': 300,
})

output_dir = "/Users/promaa/Documents/kaust-5G-research/docs/obsidian/KAUST INTERNSHIP/pres1"

# ==============================================================================
# Graph 1: Bande passante USB
# ==============================================================================
def create_bandwidth():
    fig, ax = plt.subplots(figsize=(8, 4))
    
    labels = ['Théorique\n(USB 3.2)', 'x86 Mini-PC', 'Jetson Orin\n(Mesuré)', '5G NR\nMinimum']
    values = [10, 7, 3, 4.5]
    colors = ['#4CAF50', '#2196F3', '#F44336', '#9C27B0']
    
    ax.bar(labels, values, color=colors, width=0.5, edgecolor='black', linewidth=0.5)
    
    for i, v in enumerate(values):
        ax.text(i, v + 0.3, f'{v} Gbps', ha='center', fontsize=10, fontweight='bold')
    
    ax.set_ylabel('Bande passante (Gbps)')
    ax.set_title('Comparaison bande passante USB 3.2')
    ax.set_ylim(0, 12)
    ax.axhline(y=4.5, color='red', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/graph1_bandwidth_comparison.png', facecolor='white')
    plt.close()
    print("Créé: graph1_bandwidth_comparison.png")

# ==============================================================================
# Graph 2: Alimentation USB Jetson
# ==============================================================================
def create_usb_power():
    fig, ax = plt.subplots(figsize=(7, 4))
    
    time = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    voltage = [5, 5, 5, 5, 3, 1.5, 0.5, 0, 0]
    
    ax.plot(time, voltage, 'r-o', linewidth=2.5, markersize=10)
    
    ax.set_ylim(0, 6)
    ax.set_xlabel('Temps (ms)')
    ax.set_ylabel('Tension VBUS USB (V)')
    ax.set_title('Jetson Orin Nano: Chute de tension USB due au SC7', fontweight='bold', fontsize=11)
    
    ax.text(1, 5.3, '5V', fontsize=10)
    ax.text(7.5, 0.3, '0V', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/graph2_usb_power_comparison.png', facecolor='white')
    plt.close()
    print("Créé: graph2_usb_power_comparison.png")

# ==============================================================================
# Graph 5: Comparaison matérielle
# ==============================================================================
def create_comparison():
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.set_title('Comparaison Matériel: Jetson Orin Nano vs x86 Mini-PC', 
                 fontsize=13, fontweight='bold', pad=15, y=0.98)
    
    # En-tête
    headers = ['Fonction', 'Jetson Orin Nano', 'x86 Mini-PC']
    x_positions = [0.5, 3, 6]
    widths = [2.5, 3, 3]
    
    for h, x, w in zip(headers, x_positions, widths):
        rect = patches.Rectangle((x, 9.2), w, 0.7, facecolor='#333333', edgecolor='black', linewidth=0.5)
        ax.add_patch(rect)
        ax.text(x + w/2, 9.55, h, ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    
    # Données
    data = [
        ('Architecture', 'ARM Cortex-A78AE', 'Intel Core i7-1360P', 'neutral'),
        ('ISA Baseband', 'NEON (SIMDE)', 'AVX-512 natif', 'neutral'),
        ('Alimentation USB', 'Mobile (SC7)', 'Desktop (Stable)', 'fail'),
        ('Débit DMA', '~3 Gbps', '5-8 Gbps', 'fail'),
        ('Canal Max', '<40 MHz', '80-100 MHz', 'fail'),
        ('5G NR Conforme', 'NON', 'OUI', 'fail'),
    ]
    
    for row_idx, (feature, jetson_val, x86_val, status) in enumerate(data):
        y = 8 - row_idx * 1.3
        
        # Colonne fonction
        rect = patches.Rectangle((0.5, y), 2.5, 1.1, facecolor='#E8E8E8', edgecolor='black', linewidth=0.5)
        ax.add_patch(rect)
        ax.text(1.75, y + 0.55, feature, ha='center', va='center', fontsize=9, fontweight='bold')
        
        # Colonne Jetson
        if status == 'fail':
            rect = patches.Rectangle((3, y), 3, 1.1, facecolor='#FFDDDD', edgecolor='black', linewidth=0.5)
            ax.add_patch(rect)
            ax.text(4.5, y + 0.55, jetson_val, ha='center', va='center', fontsize=9, color='#AA0000', fontweight='bold')
        else:
            rect = patches.Rectangle((3, y), 3, 1.1, facecolor='#F5F5F5', edgecolor='black', linewidth=0.5)
            ax.add_patch(rect)
            ax.text(4.5, y + 0.55, jetson_val, ha='center', va='center', fontsize=9, color='#333333')
        
        # Colonne x86
        if status == 'fail':
            rect = patches.Rectangle((6, y), 3, 1.1, facecolor='#DDFFDD', edgecolor='black', linewidth=0.5)
            ax.add_patch(rect)
            ax.text(7.5, y + 0.55, x86_val, ha='center', va='center', fontsize=9, color='#006600', fontweight='bold')
        else:
            rect = patches.Rectangle((6, y), 3, 1.1, facecolor='#F5F5F5', edgecolor='black', linewidth=0.5)
            ax.add_patch(rect)
            ax.text(7.5, y + 0.55, x86_val, ha='center', va='center', fontsize=9, color='#333333')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/graph5_hardware_comparison.png', facecolor='white', bbox_inches='tight', pad_inches=0.3)
    plt.close()
    print("Créé: graph5_hardware_comparison.png")

# ==============================================================================
# Graph 6: Benchmark CPU
# ==============================================================================
def create_benchmark():
    fig, ax = plt.subplots(figsize=(10, 5))
    
    cpus = [
        'Jetson\nOrin Nano',
        'Intel i5-1235U\n(NUC 12)', 
        'Intel i7-1360P\n(NUC 13)',
        'AMD Ryzen 7\n7735U'
    ]
    
    scores = [380, 1400, 1850, 1680]
    colors = ['#FF6B6B', '#4ECDC4', '#4ECDC4', '#4ECDC4']
    
    x = np.arange(len(cpus))
    bars = ax.bar(x, scores, color=colors, width=0.6, edgecolor='black', linewidth=0.5)
    
    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
               f'{score}', ha='center', fontsize=11, fontweight='bold')
    
    ax.set_ylabel('Score Performance Mono-cœur')
    ax.set_title('Comparaison Performance CPU\n(Plus élevé = Meilleur)', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(cpus)
    ax.set_ylim(0, 2300)
    
    ax.bar([-1], [0], color='#4ECDC4', label='x86 Mini-PC')
    ax.bar([-1], [0], color='#FF6B6B', label='ARM (Jetson)')
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/graph6_benchmark_comparison.png', facecolor='white')
    plt.close()
    print("Créé: graph6_benchmark_comparison.png")

# ==============================================================================
# Main
# ==============================================================================
if __name__ == "__main__":
    create_bandwidth()
    create_usb_power()
    create_comparison()
    create_benchmark()
    print("Tous les graphiques générés!")