import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Premium color palette (Tailwind-like Dark Mode)
BG_COLOR = "#0f172a"
CARD_BG = "#1e293b"
STROKE = "#334155"
TEXT_HEADING = "#f8fafc"
TEXT_BODY = "#94a3b8"
PRIMARY = "#3b82f6"
SUCCESS = "#10b981"
WARNING = "#f59e0b"
DANGER = "#ef4444"

# Set global styles
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.facecolor'] = BG_COLOR
plt.rcParams['savefig.facecolor'] = BG_COLOR
plt.rcParams['axes.facecolor'] = BG_COLOR

def create_shadow_box(ax, xy, width, height, color, label, icon=None, pad=0.1, subtext=None, border=STROKE, sub_alpha=0.6):
    # Shadow
    ax.add_patch(patches.FancyBboxPatch((xy[0]+0.05, xy[1]-0.05), width, height, 
                                        boxstyle=f"round,pad={pad}", color="#000000", alpha=0.3))
    # Main Box
    ax.add_patch(patches.FancyBboxPatch(xy, width, height, 
                                        boxstyle=f"round,pad={pad}", facecolor=color, edgecolor=border, lw=2))
    # Text
    center_y = xy[1] + height/2 + (0.1 if subtext else 0)
    ax.text(xy[0] + width/2, center_y, label, color=TEXT_HEADING, fontsize=14, fontweight='bold', ha='center', va='center')
    if subtext:
        ax.text(xy[0] + width/2, xy[1] + height/2 - 0.25, subtext, color=TEXT_BODY, fontsize=10, ha='center', va='center', alpha=sub_alpha)

def _box(ax, x, y, w, h, color, border_color, label, sublabel=None, fontsize=13):
    """Draw a simple rounded box with centered text. No shadows."""
    ax.add_patch(patches.FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0.12", facecolor=color, edgecolor=border_color, lw=2.5))
    cy = y + h/2 + (0.15 if sublabel else 0)
    ax.text(x + w/2, cy, label, color=TEXT_HEADING, fontsize=fontsize, fontweight='bold', ha='center', va='center')
    if sublabel:
        ax.text(x + w/2, y + h/2 - 0.2, sublabel, color=TEXT_BODY, fontsize=10, ha='center', va='center')

def arch_diagram():
    fig, ax = plt.subplots(figsize=(18, 7), dpi=300)
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 7)
    ax.axis("off")

    # Title
    ax.text(9, 6.5, "OAI 5G Network Architecture", color=TEXT_HEADING, fontsize=22, fontweight='bold', ha='center')

    # ── Column 1 (x 0.5–5): Core Machine ──
    ax.add_patch(patches.FancyBboxPatch((0.5, 0.5), 4.5, 5.2,
                 boxstyle="round,pad=0.15", facecolor=CARD_BG, edgecolor=PRIMARY, lw=2))
    ax.text(2.75, 5.35, "Core Machine (oai-pc)", color=PRIMARY, fontsize=14, fontweight='bold', ha='center')
    ax.text(2.75, 5.0, "10.85.143.198", color=TEXT_BODY, fontsize=10, ha='center')

    _box(ax, 1.0, 4.0, 3.5, 0.7, "#064e3b", SUCCESS, "AMF", ".132", fontsize=12)
    _box(ax, 1.0, 3.0, 3.5, 0.7, "#064e3b", SUCCESS, "SMF", ".133", fontsize=12)
    _box(ax, 1.0, 2.0, 3.5, 0.7, "#064e3b", SUCCESS, "UPF", ".134", fontsize=12)

    _box(ax, 1.0, 0.9, 1.5, 0.7, "#3b1010", DANGER, "SCTP Proxy", ":38412", fontsize=10)
    _box(ax, 3.0, 0.9, 1.5, 0.7, "#3b1010", DANGER, "HTTP Proxy", ":8080", fontsize=10)

    # ── Arrow lane 1 (x 5–7): Core ↔ University ──
    ax.annotate("", xy=(7, 3.5), xytext=(5, 3.5),
               arrowprops=dict(arrowstyle="<->", color=SUCCESS, lw=3))
    ax.text(6.0, 4.0, "N2 · SCTP", color=SUCCESS, fontsize=11, fontweight='bold', ha='center')
    ax.text(6.0, 3.0, "✓ Working", color=SUCCESS, fontsize=10, ha='center')

    # ── Column 2 (x 7–11): University Network ──
    _box(ax, 7, 2.6, 4, 1.8, CARD_BG, STROKE, "University\nNetwork", "WiFi  ·  10.85.x.x", fontsize=14)

    # ── Arrow lane 2 (x 11–13): University ↔ Jetson ──
    ax.annotate("", xy=(13, 3.5), xytext=(11, 3.5),
               arrowprops=dict(arrowstyle="<->", color=DANGER, lw=3, linestyle='--'))
    ax.text(12.0, 4.0, "SCTP", color=DANGER, fontsize=11, fontweight='bold', ha='center')
    ax.text(12.0, 3.0, "✗ Blocked", color=DANGER, fontsize=10, ha='center')

    # ── Column 3 (x 13–17.5): Jetson Orin Nano ──
    ax.add_patch(patches.FancyBboxPatch((13, 0.5), 4.5, 5.2,
                 boxstyle="round,pad=0.15", facecolor=CARD_BG, edgecolor=WARNING, lw=2))
    ax.text(15.25, 5.35, "Jetson Orin Nano", color=WARNING, fontsize=14, fontweight='bold', ha='center')
    ax.text(15.25, 5.0, "10.85.156.17", color=TEXT_BODY, fontsize=10, ha='center')

    _box(ax, 13.5, 3.5, 3.5, 1.0, "#3b1010", DANGER, "gNB (DU)", "SCTP required", fontsize=13)
    _box(ax, 13.5, 1.5, 3.5, 1.2, CARD_BG, DANGER, "Kernel 5.15.148-tegra", "No SCTP module", fontsize=11)

    plt.tight_layout()
    plt.savefig('arch_diagram.png', bbox_inches='tight')
    plt.close()

def jetson_sctp_error():
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")
    
    # Terminal Window
    create_shadow_box(ax, (0.5, 0.5), 9, 4, "#000000", "", border=STROKE)
    
    # macOS style buttons
    ax.add_patch(patches.Circle((0.8, 4.2), 0.08, color="#ef4444"))
    ax.add_patch(patches.Circle((1.1, 4.2), 0.08, color="#f59e0b"))
    ax.add_patch(patches.Circle((1.4, 4.2), 0.08, color="#10b981"))
    
    # Text inside terminal
    lines = [
        ("$ sudo modprobe sctp", SUCCESS),
        ("FATAL: Module sctp not found in directory /lib/modules/5.15.148-tegra", DANGER),
        ("", TEXT_HEADING),
        ("$ socat SCTP-LISTEN:38412,fork /dev/null", SUCCESS),
        ("socat[123]: E Protocol not supported", DANGER),
    ]
    
    y = 3.5
    for text, color in lines:
        ax.text(0.8, y, text, color=color, fontsize=12, fontfamily='monospace', va='center')
        y -= 0.4
        
    # Root Cause badge
    create_shadow_box(ax, (5, 0.8), 4, 1.2, CARD_BG, "Root Cause", subtext="NVIDIA Jetson Kernel lacks SCTP build.\nRequires custom toolchain recompilation.", border=PRIMARY)
    
    plt.tight_layout()
    plt.savefig('jetson_sctp_error.png', bbox_inches='tight')
    plt.close()

def progress_timeline():
    fig, ax = plt.subplots(figsize=(12, 4), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4)
    ax.axis("off")
    
    ax.text(6, 3.5, "Project Progress", color=TEXT_HEADING, fontsize=24, fontweight='bold', ha='center')
    
    # Timeline line
    ax.plot([1.5, 10.5], [2, 2], color=STROKE, lw=4, zorder=0)
    
    phases = [
        (2.5, "Phase 1: Setup", "SCTP proxy & OAI-CN", SUCCESS, "COMPLETED"),
        (6.0, "Phase 2: Ethernet", "Direct subnet routing", PRIMARY, "PENDING"),
        (9.5, "Phase 3: RF", "USRP B210 integration", WARNING, "PENDING")
    ]
    
    for x, title, sub, color, status in phases:
        ax.add_patch(patches.Circle((x, 2), 0.4, color=color, zorder=10))
        create_shadow_box(ax, (x-1.5, 0.5), 3, 1, CARD_BG, title, subtext=sub, border=color)
        
        # Status pill
        bx = x-0.6
        bw = 1.2
        by = 2.6
        ax.add_patch(patches.FancyBboxPatch((bx, by), bw, 0.4, boxstyle="round,pad=0.05", facecolor=color, edgecolor="none", zorder=10))
        ax.text(x, by+0.2, status, color=TEXT_HEADING, fontsize=9, fontweight='bold', ha='center', va='center')
        
    plt.tight_layout()
    plt.savefig('progress_timeline.png', bbox_inches='tight')
    plt.close()

def summary_status():
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")

    ax.text(6, 5.5, "Summary", color=TEXT_HEADING, fontsize=22, fontweight='bold', ha='center')

    # ── LEFT: What Works ──
    # Header bar
    ax.add_patch(patches.FancyBboxPatch((0.5, 4.3), 5, 0.6,
                 boxstyle="round,pad=0.08", facecolor=SUCCESS, edgecolor='none'))
    ax.text(3.0, 4.6, "WHAT WORKS", color='white', fontsize=14, fontweight='bold', ha='center', va='center')
    # Card body
    ax.add_patch(patches.FancyBboxPatch((0.5, 0.5), 5, 3.7,
                 boxstyle="round,pad=0.1", facecolor=CARD_BG, edgecolor=SUCCESS, lw=1.5))

    works = [
        "5G Core Network — all containers healthy",
        "SCTP Proxy — relays :38412 to AMF",
        "HTTP Proxy — relays :8080 to AMF",
        "University network path verified",
        "Core machine gNB attached & running",
        "UE connected — IP 12.1.1.2",
    ]
    y = 3.8
    for item in works:
        ax.text(1.0, y, "✓  " + item, color=SUCCESS, fontsize=11, va='center')
        y -= 0.5

    # ── RIGHT: Blocked ──
    ax.add_patch(patches.FancyBboxPatch((6.5, 4.3), 5, 0.6,
                 boxstyle="round,pad=0.08", facecolor=DANGER, edgecolor='none'))
    ax.text(9.0, 4.6, "BLOCKED", color='white', fontsize=14, fontweight='bold', ha='center', va='center')
    ax.add_patch(patches.FancyBboxPatch((6.5, 0.5), 5, 3.7,
                 boxstyle="round,pad=0.1", facecolor=CARD_BG, edgecolor=DANGER, lw=1.5))

    blocked = [
        "Jetson Orin Nano — offline",
        "Kernel 5.15.148 — no SCTP module",
        "N2 interface (gNB → AMF) — blocked",
        "F1-C interface (CU ↔ DU) — blocked",
        "Toolchain mismatch — modprobe fails",
    ]
    y = 3.8
    for item in blocked:
        ax.text(7.0, y, "✗  " + item, color=DANGER, fontsize=11, va='center')
        y -= 0.5

    # Recommendation bar at bottom
    ax.add_patch(patches.FancyBboxPatch((2.5, 0.05), 7, 0.4,
                 boxstyle="round,pad=0.06", facecolor=PRIMARY, edgecolor='none'))
    ax.text(6, 0.25, "Workaround: use core machine gNB for demo", color='white', fontsize=11, fontweight='bold', ha='center', va='center')

    plt.tight_layout()
    plt.savefig('summary_status.png', bbox_inches='tight')
    plt.close()

print("Generating visuals...")
arch_diagram()
jetson_sctp_error()
progress_timeline()
summary_status()
print("All pngs created.")