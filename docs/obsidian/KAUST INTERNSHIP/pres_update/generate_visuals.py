#!/usr/bin/env python3
"""
Generate clean, professional visual diagrams for OAI 5G presentation
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
import matplotlib.lines as mlines
import numpy as np

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11

# ============ Figure 1: Network Architecture (Clean) ============
fig1, ax1 = plt.subplots(figsize=(13, 7))
ax1.set_xlim(0, 13)
ax1.set_ylim(0, 8)
ax1.axis('off')
fig1.patch.set_facecolor('#fafafa')

# Title
ax1.text(6.5, 7.5, 'OpenAirInterface 5G: Network Architecture', fontsize=20, fontweight='bold', ha='center', color='#1a1a2e')

# ============ CORE MACHINE ============
# Main box
core = FancyBboxPatch((0.5, 1.5), 4.5, 5, boxstyle="round,pad=0.1",
                       facecolor='white', edgecolor='#3498db', linewidth=3)
ax1.add_patch(core)

# Header
header_core = FancyBboxPatch((0.5, 6), 4.5, 0.5, boxstyle="round,pad=0.05",
                              facecolor='#3498db', edgecolor='#2980b9', linewidth=2)
ax1.add_patch(header_core)
ax1.text(2.75, 6.25, 'CORE MACHINE (oai-pc)', fontsize=11, fontweight='bold', ha='center', color='white')

# IP
ax1.text(2.75, 5.5, '10.85.143.198', fontsize=10, ha='center', color='#7f8c8d', style='italic')

# Docker section label
ax1.add_patch(Rectangle((0.8, 4.5), 4, 0.8, facecolor='#9b59b6', alpha=0.15))
ax1.text(2.75, 4.85, 'Docker Network (192.168.71.128/26)', fontsize=9, ha='center', color='#8e44ad', fontweight='bold')

# Containers - horizontal layout
containers = [
    ('AMF', '192.168.71.132'),
    ('SMF', '192.168.71.133'),
    ('UPF', '192.168.71.134'),
]
for i, (name, ip) in enumerate(containers):
    x = 1.0 + i * 1.35
    c = FancyBboxPatch((x, 4.55), 1.15, 0.65, boxstyle="round,pad=0.05",
                       facecolor='#27ae60', edgecolor='#219a52', linewidth=1.5)
    ax1.add_patch(c)
    ax1.text(x + 0.575, 4.98, name, fontsize=9, ha='center', color='white', fontweight='bold')
    ax1.text(x + 0.575, 4.7, ip.split('.')[-1], fontsize=7, ha='center', color='#d5f5e3')

# Proxy section label
ax1.add_patch(Rectangle((0.8, 2.7), 4, 0.8, facecolor='#f39c12', alpha=0.15))
ax1.text(2.75, 3.05, 'Python Proxies', fontsize=9, ha='center', color='#d68910', fontweight='bold')

# Proxies - horizontal
proxies = [('SCTP Proxy', ':38412', '#e74c3c'), ('HTTP Proxy', ':8080', '#c0392b')]
for i, (name, port, color) in enumerate(proxies):
    x = 1.0 + i * 2.0
    p = FancyBboxPatch((x, 2.8), 1.7, 0.7, boxstyle="round,pad=0.05",
                       facecolor=color, edgecolor='#c0392b', linewidth=1.5)
    ax1.add_patch(p)
    ax1.text(x + 0.85, 3.2, name, fontsize=8, ha='center', color='white', fontweight='bold')
    ax1.text(x + 0.85, 2.95, port, fontsize=7, ha='center', color='white')

# ============ UNIVERSITY NETWORK ============
ax1.add_patch(FancyBboxPatch((5.5, 3.5), 2.5, 2, boxstyle="round,pad=0.1",
                            facecolor='#ecf0f1', edgecolor='#95a5a6', linewidth=2))
ax1.text(6.75, 5.1, 'University', fontsize=12, fontweight='bold', ha='center', color='#2c3e50')
ax1.text(6.75, 4.7, 'Network', fontsize=12, fontweight='bold', ha='center', color='#2c3e50')
ax1.text(6.75, 4.2, '10.85.x.x', fontsize=9, ha='center', color='#7f8c8d', style='italic')
ax1.text(6.75, 3.8, 'WiFi', fontsize=9, ha='center', color='#95a5a6')

# ============ JETSON ============
jetson = FancyBboxPatch((8.5, 1.5), 4, 5, boxstyle="round,pad=0.1",
                         facecolor='white', edgecolor='#e74c3c', linewidth=3)
ax1.add_patch(jetson)

header_jetson = FancyBboxPatch((8.5, 6), 4, 0.5, boxstyle="round,pad=0.05",
                                facecolor='#e74c3c', edgecolor='#c0392b', linewidth=2)
ax1.add_patch(header_jetson)
ax1.text(10.5, 6.25, 'JETSON ORIN NANO', fontsize=11, fontweight='bold', ha='center', color='white')

ax1.text(10.5, 5.5, '10.85.156.17', fontsize=10, ha='center', color='#7f8c8d', style='italic')

# gNB Docker
gnb = FancyBboxPatch((8.8, 4.3), 3.4, 1.0, boxstyle="round,pad=0.05",
                     facecolor='white', edgecolor='#e74c3c', linewidth=2)
ax1.add_patch(gnb)
ax1.text(10.5, 4.95, 'gNB Docker', fontsize=10, ha='center', color='#e74c3c', fontweight='bold')
ax1.text(10.5, 4.6, 'oai-gnb:develop', fontsize=8, ha='center', color='#7f8c8d')
ax1.text(10.5, 4.25, 'SCTP: BLOCKED', fontsize=9, ha='center', color='#e74c3c', fontweight='bold')

# Error
err = FancyBboxPatch((8.8, 2.5), 3.4, 1.4, boxstyle="round,pad=0.05",
                     facecolor='#fadbd8', edgecolor='#e74c3c', linewidth=2)
ax1.add_patch(err)
ax1.text(10.5, 3.5, 'ERROR', fontsize=10, ha='center', color='#c0392b', fontweight='bold')
ax1.text(10.5, 3.1, 'Kernel 5.15.148-tegra', fontsize=8, ha='center', color='#922b21')
ax1.text(10.5, 2.75, 'No SCTP Support', fontsize=8, ha='center', color='#922b21')

# ============ ARROWS ============
# Core <-> University
ax1.annotate('', xy=(5.5, 4.8), xytext=(5, 4.8),
            arrowprops=dict(arrowstyle='<->', color='#27ae60', lw=2.5, shrinkA=5, shrinkB=5))
ax1.text(5.25, 5.05, 'N2', fontsize=9, ha='center', color='#27ae60', fontweight='bold')

# University <-> Jetson
ax1.annotate('', xy=(8.5, 4.8), xytext=(8, 4.8),
            arrowprops=dict(arrowstyle='<->', color='#95a5a6', lw=2.5, shrinkA=5, shrinkB=5))
ax1.text(8.25, 5.05, 'WiFi', fontsize=9, ha='center', color='#95a5a6')

# Legend
ax1.add_patch(Circle((1, 0.8), 0.15, facecolor='#27ae60', edgecolor='none'))
ax1.text(1.3, 0.8, 'Working', fontsize=10, va='center')
ax1.add_patch(Circle((3, 0.8), 0.15, facecolor='#e74c3c', edgecolor='none'))
ax1.text(3.3, 0.8, 'Blocked', fontsize=10, va='center')

plt.tight_layout()
plt.savefig('/home/oai/kaust-5G-research/docs/obsidian/KAUST INTERNSHIP/pres_update/arch_diagram.png', dpi=200, bbox_inches='tight', facecolor='#fafafa')
print("Saved: arch_diagram.png")
plt.close()


# ============ Figure 2: Jetson SCTP Error (Clean Terminal) ============
fig2, ax2 = plt.subplots(figsize=(12, 4))
ax2.set_xlim(0, 12)
ax2.set_ylim(0, 5)
ax2.axis('off')
fig2.patch.set_facecolor('#1e1e1e')

# Terminal frame
terminal = FancyBboxPatch((0.2, 0.3), 11.6, 4.4, boxstyle="round,pad=0.08",
                           facecolor='#1e1e1e', edgecolor='#444', linewidth=2)
ax2.add_patch(terminal)

# Title bar
titlebar = FancyBboxPatch((0.2, 4.35), 11.6, 0.35, boxstyle="round,pad=0.02",
                           facecolor='#2d2d2d', edgecolor='#444')
ax2.add_patch(titlebar)

# Window dots
for i, (x, c) in enumerate([(0.5, '#ff5f56'), (0.75, '#ffbd2e'), (1.0, '#27ca3f')]):
    ax2.add_patch(Circle((x, 4.52), 0.08, facecolor=c, edgecolor='none'))
ax2.text(6, 4.52, 'jetson@uav-bs: SCTP Test', fontsize=10, color='#aaa', ha='center', va='center')

# Commands - cleaner layout
y = 4.0
commands = [
    ('$ sudo cat /proc/net/sctp/eps', None, '#fff'),
    ('cat: /proc/net/sctp/eps: No such file or directory', 1, '#e74c3c'),
    ('', None, '#fff'),
    ('$ sudo modprobe sctp', None, '#fff'),
    ('FATAL: Module sctp not found in directory', 1, '#e74c3c'),
    ('/lib/modules/5.15.148-tegra', 1, '#e74c3c'),
    ('', None, '#fff'),
    ('$ socat SCTP-LISTEN:38412,fork /dev/null', None, '#fff'),
    ('socat E socket(2, 1, 132): Protocol not supported', 1, '#e74c3c'),
    ('', None, '#fff'),
    ('$ python3 -c "import socket; socket.socket(\\', None, '#fff'),
    ('    AF_INET, SOCK_STREAM, IPPROTO_SCTP)"', None, '#fff'),
    ('OSError: [Errno 92] Protocol not available', 1, '#e74c3c'),
]

for cmd, indent, color in commands:
    if indent:
        ax2.text(1.0, y, cmd, fontsize=9, color=color, family='monospace')
    else:
        ax2.text(0.5, y, cmd, fontsize=9, color=color, family='monospace')
    y -= 0.26

# Root cause box
rc = FancyBboxPatch((7.5, 0.5), 4.2, 1.0, boxstyle="round,pad=0.1",
                     facecolor='#c0392b', edgecolor='#922b21', linewidth=2)
ax2.add_patch(rc)
ax2.text(9.6, 1.2, 'ROOT CAUSE', fontsize=10, ha='center', color='white', fontweight='bold')
ax2.text(9.6, 0.85, 'Kernel lacks SCTP module', fontsize=9, ha='center', color='white')
ax2.text(9.6, 0.5, '5G N2 and F1-C require SCTP', fontsize=8, ha='center', color='#fadbd8', style='italic')

plt.tight_layout()
plt.savefig('/home/oai/kaust-5G-research/docs/obsidian/KAUST INTERNSHIP/pres_update/jetson_sctp_error.png', dpi=200, bbox_inches='tight', facecolor='#1e1e1e')
print("Saved: jetson_sctp_error.png")
plt.close()


# ============ Figure 3: Progress Timeline ============
fig3, ax3 = plt.subplots(figsize=(12, 4.5))
ax3.set_xlim(0, 12)
ax3.set_ylim(0, 5)
ax3.axis('off')
fig3.patch.set_facecolor('white')

# Title
ax3.text(6, 4.5, 'Project Progress', fontsize=20, fontweight='bold', ha='center', color='#1a1a2e')

# Timeline line
line = mlines.Line2D([1.5, 10.5], [2.2, 2.2], color='#bdc3c7', lw=5, solid_capstyle='round')
ax3.add_line(line)

# Phases
phases = [
    ('1', 'Phase 1', 'Network Setup', '#27ae60', 'COMPLETED', [
        'OAI-CN deployed',
        'Proxies working',
        'Path verified'
    ]),
    ('2', 'Phase 2', 'Direct Ethernet', '#3498db', 'PENDING', [
        'Cable connection',
        'Isolated subnet',
        'NAT config'
    ]),
    ('3', 'Phase 3', 'USRP B210', '#9b59b6', 'PENDING', [
        'Hardware',
        'Real RF',
        'Demo'
    ]),
]

x_pos = [2.5, 6, 9.5]

for i, (num, title, subtitle, color, status, bullets) in enumerate(phases):
    x = x_pos[i]

    # Circle
    circle = Circle((x, 2.2), 0.35, facecolor=color, edgecolor='white', linewidth=4)
    ax3.add_patch(circle)
    ax3.text(x, 2.2, num, fontsize=18, fontweight='bold', ha='center', va='center', color='white')

    # Title
    ax3.text(x, 3.0, title, fontsize=12, fontweight='bold', ha='center', color='#1a1a2e')
    ax3.text(x, 2.6, subtitle, fontsize=10, ha='center', color='#7f8c8d')

    # Status badge
    badge_color = '#27ae60' if status == 'COMPLETED' else '#95a5a6'
    badge = FancyBboxPatch((x-0.55, 1.0), 1.1, 0.35, boxstyle="round,pad=0.05",
                            facecolor=badge_color, edgecolor='white', linewidth=1)
    ax3.add_patch(badge)
    ax3.text(x, 1.175, status, fontsize=8, ha='center', va='center', color='white', fontweight='bold')

    # Bullets
    for j, b in enumerate(bullets):
        ax3.text(x - 0.6, 0.65 - j*0.22, b, fontsize=8, color='#34495e', ha='center')

# Current arrow
ax3.annotate('', xy=(2.5, 3.3), xytext=(2.5, 3.1),
              arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=2))
ax3.text(2.5, 3.45, 'CURRENT', fontsize=8, ha='center', color='#e74c3c', fontweight='bold')

plt.tight_layout()
plt.savefig('/home/oai/kaust-5G-research/docs/obsidian/KAUST INTERNSHIP/pres_update/progress_timeline.png', dpi=200, bbox_inches='tight', facecolor='white')
print("Saved: progress_timeline.png")
plt.close()


# ============ Figure 4: Summary - What Works / Blocked ============
fig4, ax4 = plt.subplots(figsize=(12, 4.5))
ax4.set_xlim(0, 12)
ax4.set_ylim(0, 5)
ax4.axis('off')
fig4.patch.set_facecolor('white')

# Title
ax4.text(6, 4.5, 'Summary: Current Status', fontsize=20, fontweight='bold', ha='center', color='#1a1a2e')

# LEFT - WORKS
works = FancyBboxPatch((0.5, 0.6), 5.2, 3.4, boxstyle="round,pad=0.1",
                       facecolor='#d5f5e3', edgecolor='#27ae60', linewidth=3)
ax4.add_patch(works)

header_w = FancyBboxPatch((0.5, 3.6), 5.2, 0.4, boxstyle="round,pad=0.05",
                           facecolor='#27ae60', edgecolor='#219a52', linewidth=2)
ax4.add_patch(header_w)
ax4.text(3.1, 3.8, 'WHAT WORKS', fontsize=12, fontweight='bold', ha='center', color='white')

works_items = [
    ('OAI-CN 5G Core Network', 'All containers healthy'),
    ('SCTP Proxy', '0.0.0.0:38412 -> AMF'),
    ('HTTP Proxy', '0.0.0.0:8080 -> AMF:80'),
    ('University Network Path', 'SCTP verified in AMF logs'),
    ('Core Machine gNB', 'rfsim5g-oai-gnb running'),
]

for i, (title, desc) in enumerate(works_items):
    y = 3.2 - i * 0.52
    ax4.text(0.8, y, '+', fontsize=14, color='#27ae60', fontweight='bold')
    ax4.text(1.1, y, title, fontsize=10, color='#1a1a2e', fontweight='bold')
    ax4.text(1.1, y - 0.22, desc, fontsize=8, color='#7f8c8d', style='italic')

# RIGHT - BLOCKED
blocked = FancyBboxPatch((6.3, 0.6), 5.2, 3.4, boxstyle="round,pad=0.1",
                         facecolor='#fadbd8', edgecolor='#e74c3c', linewidth=3)
ax4.add_patch(blocked)

header_b = FancyBboxPatch((6.3, 3.6), 5.2, 0.4, boxstyle="round,pad=0.05",
                          facecolor='#e74c3c', edgecolor='#c0392b', linewidth=2)
ax4.add_patch(header_b)
ax4.text(8.9, 3.8, 'BLOCKED', fontsize=12, fontweight='bold', ha='center', color='white')

blocked_items = [
    ('Jetson gNB', 'No SCTP in kernel'),
    ('Jetson CU/DU', 'F1-C requires SCTP'),
    ('Jetson N2', 'gNB->AMF requires SCTP'),
]

for i, (title, desc) in enumerate(blocked_items):
    y = 3.2 - i * 0.52
    ax4.text(6.6, y, 'X', fontsize=12, color='#e74c3c', fontweight='bold')
    ax4.text(6.9, y, title, fontsize=10, color='#c0392b', fontweight='bold')
    ax4.text(6.9, y - 0.22, desc, fontsize=8, color='#7f8c8d', style='italic')

# Recommendation
rec = FancyBboxPatch((3.5, 0.15), 5, 0.35, boxstyle="round,pad=0.05",
                     facecolor='#3498db', edgecolor='#2980b9', linewidth=2)
ax4.add_patch(rec)
ax4.text(6, 0.325, 'RECOMMENDATION: Use x86 Mini-PC for RAN', fontsize=10, ha='center', color='white', fontweight='bold')

plt.tight_layout()
plt.savefig('/home/oai/kaust-5G-research/docs/obsidian/KAUST INTERNSHIP/pres_update/summary_status.png', dpi=200, bbox_inches='tight', facecolor='white')
print("Saved: summary_status.png")
plt.close()


print("\nAll graphics generated successfully!")